/**
 * ParikshaSetu CBT Examination Engine
 * Handles client-side test state, timer countdown, question navigation,
 * palette indicators, review flagging, and secure submission.
 */

class CbtEngine {
  constructor(config) {
    this.questions = config.questions || [];
    this.attemptId = config.attemptId;
    this.durationMinutes = config.durationMinutes || 90;
    this.submitUrl = config.submitUrl;
    this.currentIdx = 0;
    
    // State maps
    this.selectedAnswers = {}; // { questionId: optionIndex }
    this.markedForReview = {}; // { questionId: boolean }
    this.visitedQuestions = {}; // { questionId: boolean }

    this.timerSeconds = this.durationMinutes * 60;
    this.timerInterval = null;
    this.timeTakenSeconds = 0;

    this.init();
  }

  init() {
    if (this.questions.length === 0) {
      alert("No questions available for this paper.");
      return;
    }

    this.renderQuestionPalette();
    this.loadQuestion(0);
    this.startTimer();
    this.bindEvents();
    this.updateStats();
  }

  startTimer() {
    const timerDisplay = document.getElementById('cbt-timer-display');
    const startTime = Date.now();
    const totalSecs = this.timerSeconds;

    this.timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      this.timeTakenSeconds = elapsed;
      const remaining = Math.max(0, totalSecs - elapsed);

      const hours = Math.floor(remaining / 3600);
      const minutes = Math.floor((remaining % 3600) / 60);
      const seconds = remaining % 60;

      const formatted = [
        hours > 0 ? String(hours).padStart(2, '0') : null,
        String(minutes).padStart(2, '0'),
        String(seconds).padStart(2, '0')
      ].filter(Boolean).join(':');

      if (timerDisplay) {
        timerDisplay.innerText = formatted;
        if (remaining <= 300) {
          // Warning state under 5 mins
          timerDisplay.style.borderColor = '#ef4444';
          timerDisplay.style.color = '#ef4444';
        }
      }

      if (remaining <= 0) {
        clearInterval(this.timerInterval);
        alert('वेळ संपली आहे! आपली परीक्षा स्वयंचलितरित्या जमा (Auto-Submitted) होत आहे.');
        this.submitExam(true);
      }
    }, 1000);
  }

  renderQuestionPalette() {
    const palette = document.getElementById('question-palette-container');
    if (!palette) return;

    palette.innerHTML = '';
    this.questions.forEach((q, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'palette-btn unanswered';
      btn.id = `palette-btn-${idx}`;
      btn.innerText = idx + 1;
      btn.title = `Question ${idx + 1} (${q.subject || ''})`;
      btn.addEventListener('click', () => this.loadQuestion(idx));
      palette.appendChild(btn);
    });
  }

  loadQuestion(idx) {
    if (idx < 0 || idx >= this.questions.length) return;
    this.currentIdx = idx;
    const q = this.questions[idx];
    const qid = String(q.id);

    this.visitedQuestions[qid] = true;

    // Header info
    document.getElementById('q-current-number').innerText = idx + 1;
    document.getElementById('q-total-number').innerText = this.questions.length;
    document.getElementById('q-subject-badge').innerText = q.subject || 'General';
    document.getElementById('q-topic-badge').innerText = q.topic || 'Exam Question';
    document.getElementById('q-marks').innerText = `+${q.marks || 1} / -${q.negative_marks || 0}`;

    // Question text
    document.getElementById('question-text-content').innerText = q.question_text || '';
    const enText = document.getElementById('question-text-en');
    if (enText) {
      if (q.question_text_en) {
        enText.innerText = q.question_text_en;
        enText.style.display = 'block';
      } else {
        enText.style.display = 'none';
      }
    }

    // Render Options
    const optionsContainer = document.getElementById('options-list-container');
    optionsContainer.innerHTML = '';

    const letters = ['A', 'B', 'C', 'D', 'E'];
    const currentSelection = this.selectedAnswers[qid];

    (q.options || []).forEach((opt, optIdx) => {
      const label = document.createElement('label');
      label.className = `option-label ${currentSelection === optIdx ? 'selected' : ''}`;
      label.id = `option-label-${optIdx}`;

      const radio = document.createElement('input');
      radio.type = 'radio';
      radio.name = `question_option_${qid}`;
      radio.value = optIdx;
      radio.checked = (currentSelection === optIdx);
      radio.style.marginRight = '12px';

      radio.addEventListener('change', () => {
        this.selectOption(optIdx);
      });

      const letterBadge = document.createElement('span');
      letterBadge.style.cssText = 'width: 26px; height: 26px; border-radius: 50%; background: #e2e8f0; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 12px; font-size: 0.85rem;';
      letterBadge.innerText = letters[optIdx] || optIdx + 1;

      const textSpan = document.createElement('span');
      textSpan.innerText = opt;

      label.appendChild(radio);
      label.appendChild(letterBadge);
      label.appendChild(textSpan);
      optionsContainer.appendChild(label);
    });

    // Update Nav buttons state
    document.getElementById('btn-prev-question').disabled = (idx === 0);
    const nextBtn = document.getElementById('btn-next-question');
    if (idx === this.questions.length - 1) {
      nextBtn.innerHTML = 'शेवटचा प्रश्न (Last Q)';
    } else {
      nextBtn.innerHTML = 'पुढील प्रश्न (Next) <i class="bi bi-arrow-right"></i>';
    }

    // Update Review button text/state
    const reviewBtn = document.getElementById('btn-mark-review');
    if (this.markedForReview[qid]) {
      reviewBtn.classList.add('btn-warning');
      reviewBtn.classList.remove('btn-outline-warning');
      reviewBtn.innerHTML = '<i class="bi bi-bookmark-check-fill"></i> चिन्हांकित आहे (Marked)';
    } else {
      reviewBtn.classList.remove('btn-warning');
      reviewBtn.classList.add('btn-outline-warning');
      reviewBtn.innerHTML = '<i class="bi bi-bookmark"></i> पुनरावलोकन (Review)';
    }

    this.updatePaletteButton(idx);
    this.updateStats();
  }

  selectOption(optIdx) {
    const q = this.questions[this.currentIdx];
    const qid = String(q.id);
    this.selectedAnswers[qid] = optIdx;

    // Update label classes
    document.querySelectorAll('.option-label').forEach((el, i) => {
      if (i === optIdx) {
        el.classList.add('selected');
      } else {
        el.classList.remove('selected');
      }
    });

    this.updatePaletteButton(this.currentIdx);
    this.updateStats();
  }

  clearAnswer() {
    const q = this.questions[this.currentIdx];
    const qid = String(q.id);
    delete this.selectedAnswers[qid];

    document.querySelectorAll('.option-label').forEach(el => el.classList.remove('selected'));
    document.querySelectorAll(`input[name="question_option_${qid}"]`).forEach(r => r.checked = false);

    this.updatePaletteButton(this.currentIdx);
    this.updateStats();
  }

  toggleMarkForReview() {
    const q = this.questions[this.currentIdx];
    const qid = String(q.id);
    this.markedForReview[qid] = !this.markedForReview[qid];

    this.loadQuestion(this.currentIdx);
  }

  updatePaletteButton(idx) {
    const btn = document.getElementById(`palette-btn-${idx}`);
    if (!btn) return;

    const q = this.questions[idx];
    const qid = String(q.id);

    btn.className = 'palette-btn';

    if (idx === this.currentIdx) {
      btn.classList.add('current');
    }

    if (this.markedForReview[qid]) {
      btn.classList.add('marked');
    } else if (this.selectedAnswers[qid] !== undefined) {
      btn.classList.add('answered');
    } else {
      btn.classList.add('unanswered');
    }
  }

  updateStats() {
    const total = this.questions.length;
    let answered = 0;
    let marked = 0;

    this.questions.forEach(q => {
      const qid = String(q.id);
      if (this.selectedAnswers[qid] !== undefined) answered++;
      if (this.markedForReview[qid]) marked++;
    });

    const notAnswered = total - answered;

    const elAns = document.getElementById('stat-answered-count');
    const elNotAns = document.getElementById('stat-unanswered-count');
    const elMarked = document.getElementById('stat-marked-count');
    const progressBar = document.getElementById('cbt-progress-bar');

    if (elAns) elAns.innerText = answered;
    if (elNotAns) elNotAns.innerText = notAnswered;
    if (elMarked) elMarked.innerText = marked;

    if (progressBar) {
      const pct = Math.round((answered / total) * 100);
      progressBar.style.width = `${pct}%`;
      progressBar.innerText = `${pct}%`;
    }
  }

  bindEvents() {
    document.getElementById('btn-prev-question')?.addEventListener('click', () => {
      if (this.currentIdx > 0) this.loadQuestion(this.currentIdx - 1);
    });

    document.getElementById('btn-next-question')?.addEventListener('click', () => {
      if (this.currentIdx < this.questions.length - 1) {
        this.loadQuestion(this.currentIdx + 1);
      }
    });

    document.getElementById('btn-clear-answer')?.addEventListener('click', () => {
      this.clearAnswer();
    });

    document.getElementById('btn-mark-review')?.addEventListener('click', () => {
      this.toggleMarkForReview();
    });

    document.getElementById('btn-submit-exam')?.addEventListener('click', () => {
      this.confirmAndSubmit();
    });
  }

  confirmAndSubmit() {
    const total = this.questions.length;
    const answered = Object.keys(this.selectedAnswers).length;
    const unanswered = total - answered;
    const marked = Object.values(this.markedForReview).filter(Boolean).length;

    const modalBody = document.getElementById('submit-confirm-summary');
    if (modalBody) {
      modalBody.innerHTML = `
        <div class="row g-2 text-center my-2">
          <div class="col-4">
            <div class="p-2 border rounded bg-light">
              <h5 class="mb-0 text-success fw-bold">${answered}</h5>
              <small class="text-muted">सोडवलेले (Answered)</small>
            </div>
          </div>
          <div class="col-4">
            <div class="p-2 border rounded bg-light">
              <h5 class="mb-0 text-secondary fw-bold">${unanswered}</h5>
              <small class="text-muted">न सोडवलेले (Pending)</small>
            </div>
          </div>
          <div class="col-4">
            <div class="p-2 border rounded bg-light">
              <h5 class="mb-0 text-warning fw-bold">${marked}</h5>
              <small class="text-muted">रिव्ह्यूसाठी (Marked)</small>
            </div>
          </div>
        </div>
        <p class="mt-3 text-muted">तुम्हाला खात्री आहे का की तुम्हाला परीक्षा अंतिम जमा (Final Submit) करायची आहे?</p>
      `;
    }

    const modalEl = document.getElementById('submitConfirmModal');
    if (modalEl && window.bootstrap) {
      const modal = new bootstrap.Modal(modalEl);
      modal.show();

      document.getElementById('btn-modal-final-submit').onclick = () => {
        modal.hide();
        this.submitExam(false);
      };
    } else {
      if (confirm(`एकूण प्रश्न: ${total}\nसोडवलेले: ${answered}\nन सोडवलेले: ${unanswered}\n\nतुम्हाला परीक्षा जमा करायची आहे का?`)) {
        this.submitExam(false);
      }
    }
  }

  submitExam(isAuto = false) {
    clearInterval(this.timerInterval);

    // Disable all buttons to prevent double-submit
    const submitBtn = document.getElementById('btn-submit-exam');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerText = 'गुणवत्ता तपासत आहे... (Evaluating)';
    }

    fetch(this.submitUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        answers: this.selectedAnswers,
        time_taken_seconds: this.timeTakenSeconds,
        is_auto_submit: isAuto
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
      } else {
        alert('त्रुटी: निकाल प्राप्त होऊ शकला नाही.');
      }
    })
    .catch(err => {
      console.error('Submission error:', err);
      // Fallback form submit
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = this.submitUrl;
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'answers_json';
      input.value = JSON.stringify(this.selectedAnswers);
      form.appendChild(input);

      const timeInput = document.createElement('input');
      timeInput.type = 'hidden';
      timeInput.name = 'time_taken_seconds';
      timeInput.value = this.timeTakenSeconds;
      form.appendChild(timeInput);

      document.body.appendChild(form);
      form.submit();
    });
  }
}

window.CbtEngine = CbtEngine;
