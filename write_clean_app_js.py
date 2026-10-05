# -*- coding: utf-8 -*-

app_js_code = r'''/**
 * 心理学导论 · 全章节刷题与背诵系统 (347备考)
 * Client Application Logic (Full Enhanced Version)
 */

(function () {
  'use strict';

  // State
  const state = {
    chapters: [],
    questions: [],
    currentChapterId: 1, // 1 to 18, or 'all'
    currentMode: 'practice', // 'practice', 'random', 'recite', 'wrong', 'star'
    currentFilterType: 'all', // 'all', 'choice', 'judge', 'blank', 'short'
    searchQuery: '',
    theme: 'light',
    userAnswers: {}, // { qId: { selectedOption, isCorrect, timestamp } }
    starredIds: new Set(),
    wrongIds: new Set(),
    revealedCardIds: new Set(),
    masteredIds: new Set(),

    // Random Mock Exam State
    randomQuestions: [],
    examType: 'rotation_18', // 'rotation_18', 'random_30', 'random_50'
    examStartTime: null,
    examTimerInterval: null,
    examSubmitted: false,
    examDurationFormatted: '00:00',
  };

  // DOM Elements
  const els = {
    app: document.getElementById('app'),
    currentChapterTitle: document.getElementById('current-chapter-title'),
    currentChapterSubtitle: document.getElementById('current-chapter-subtitle'),
    chapterDescBanner: document.getElementById('chapter-desc-banner'),
    chapterDescText: document.getElementById('chapter-desc-text'),
    btnToggleDiagram: document.getElementById('btn-toggle-diagram'),
    chapterDiagramBox: document.getElementById('chapter-diagram-box'),
    btnCloseDiagram: document.getElementById('btn-close-diagram'),
    diagramContent: document.getElementById('diagram-content'),
    questionsContainer: document.getElementById('questions-container'),
    emptyState: document.getElementById('empty-state'),
    btnDrawer: document.getElementById('btn-drawer'),
    drawerOverlay: document.getElementById('drawer-overlay'),
    drawerClose: document.getElementById('btn-drawer-close'),
    drawerChapterList: document.getElementById('drawer-chapter-list'),
    btnQuickNav: document.getElementById('btn-quick-nav'),
    btnPrevChapter: document.getElementById('btn-prev-chapter'),
    btnNextChapter: document.getElementById('btn-next-chapter'),
    btnTheme: document.getElementById('btn-theme'),
    themeIcon: document.getElementById('theme-icon'),
    btnSearchToggle: document.getElementById('btn-search-toggle'),
    searchBar: document.getElementById('search-bar'),
    searchInput: document.getElementById('search-input'),
    btnSearchClear: document.getElementById('btn-search-clear'),
    btnResetData: document.getElementById('btn-reset-data'),
    progressFill: document.getElementById('progress-fill'),
    statAnswered: document.getElementById('stat-answered'),
    statTotal: document.getElementById('stat-total'),
    statAccuracy: document.getElementById('stat-accuracy'),
    wrongCount: document.getElementById('wrong-count'),
    starCount: document.getElementById('star-count'),
    totalTypeCount: document.getElementById('total-type-count'),
    choiceTypeCount: document.getElementById('choice-type-count'),
    judgeTypeCount: document.getElementById('judge-type-count'),
    blankTypeCount: document.getElementById('blank-type-count'),
    shortTypeCount: document.getElementById('short-type-count'),
    modeTabs: document.querySelectorAll('.mode-tab'),
    filterChips: document.querySelectorAll('.filter-chip'),
    mainScroll: document.getElementById('main-scroll'),

    // Random Exam elements
    randomExamPanel: document.getElementById('random-exam-panel'),
    examTimer: document.getElementById('exam-timer'),
    examConfigBtns: document.querySelectorAll('.exam-config-btn'),
    btnReSample: document.getElementById('btn-re-sample'),
    btnSubmitExam: document.getElementById('btn-submit-exam'),
    examScoreModal: document.getElementById('exam-score-modal'),
    btnCloseScore: document.getElementById('btn-close-score'),
    scorePercentage: document.getElementById('score-percentage'),
    scoreAnswered: document.getElementById('score-answered'),
    scoreTotal: document.getElementById('score-total'),
    scoreCorrect: document.getElementById('score-correct'),
    scoreDuration: document.getElementById('score-duration'),
    chapterDiagnosticsList: document.getElementById('chapter-diagnostics-list'),
    btnReviewExamWrongs: document.getElementById('btn-review-exam-wrongs'),
  };

  // Local Storage Keys
  const STORAGE_KEYS = {
    THEME: 'psych_theme_pref',
    ANSWERS: 'psych_answers_data',
    STARS: 'psych_stars_data',
    WRONGS: 'psych_wrongs_data',
    MASTERED: 'psych_mastered_data',
  };

  function init() {
    loadLocalData();
    initTheme();
    bindEvents();

    if (window.QUESTIONS_DATA) {
      state.chapters = window.QUESTIONS_DATA.chapters || [];
      state.questions = window.QUESTIONS_DATA.questions || [];
    }

    renderDrawer();
    updateChapterView();
    renderQuestions();
    updateStats();
  }

  function loadLocalData() {
    try {
      const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME);
      if (savedTheme) state.theme = savedTheme;

      const savedAnswers = localStorage.getItem(STORAGE_KEYS.ANSWERS);
      if (savedAnswers) state.userAnswers = JSON.parse(savedAnswers);

      const savedStars = localStorage.getItem(STORAGE_KEYS.STARS);
      if (savedStars) state.starredIds = new Set(JSON.parse(savedStars));

      const savedWrongs = localStorage.getItem(STORAGE_KEYS.WRONGS);
      if (savedWrongs) state.wrongIds = new Set(JSON.parse(savedWrongs));

      const savedMastered = localStorage.getItem(STORAGE_KEYS.MASTERED);
      if (savedMastered) state.masteredIds = new Set(JSON.parse(savedMastered));
    } catch (e) {
      console.warn('Failed to load local storage data:', e);
    }
  }

  function saveLocalData() {
    try {
      localStorage.setItem(STORAGE_KEYS.THEME, state.theme);
      localStorage.setItem(STORAGE_KEYS.ANSWERS, JSON.stringify(state.userAnswers));
      localStorage.setItem(STORAGE_KEYS.STARS, JSON.stringify(Array.from(state.starredIds)));
      localStorage.setItem(STORAGE_KEYS.WRONGS, JSON.stringify(Array.from(state.wrongIds)));
      localStorage.setItem(STORAGE_KEYS.MASTERED, JSON.stringify(Array.from(state.masteredIds)));
    } catch (e) {
      console.warn('Failed to save to local storage:', e);
    }
  }

  function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    els.themeIcon.textContent = state.theme === 'dark' ? '☀️' : '🌙';
  }

  function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    initTheme();
    saveLocalData();
  }

  function bindEvents() {
    els.btnTheme.addEventListener('click', toggleTheme);

    // Search Toggle
    els.btnSearchToggle.addEventListener('click', () => {
      els.searchBar.classList.toggle('hidden');
      if (!els.searchBar.classList.contains('hidden')) {
        els.searchInput.focus();
      }
    });

    els.searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim().toLowerCase();
      renderQuestions();
    });

    els.btnSearchClear.addEventListener('click', () => {
      els.searchInput.value = '';
      state.searchQuery = '';
      renderQuestions();
    });

    // Drawer events
    els.btnDrawer.addEventListener('click', openDrawer);
    els.btnQuickNav.addEventListener('click', openDrawer);
    els.drawerClose.addEventListener('click', closeDrawer);
    els.drawerOverlay.addEventListener('click', (e) => {
      if (e.target === els.drawerOverlay) closeDrawer();
    });

    // Prev / Next Chapter Navigation
    els.btnPrevChapter.addEventListener('click', () => {
      if (typeof state.currentChapterId === 'number' && state.currentChapterId > 1) {
        switchChapter(state.currentChapterId - 1);
      }
    });

    els.btnNextChapter.addEventListener('click', () => {
      if (typeof state.currentChapterId === 'number' && state.currentChapterId < state.chapters.length) {
        switchChapter(state.currentChapterId + 1);
      }
    });

    // Mode Tabs
    els.modeTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        els.modeTabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        state.currentMode = tab.dataset.mode;

        if (state.currentMode === 'random') {
          enterRandomExamMode();
        } else {
          exitRandomExamMode();
        }

        updateChapterView();
        renderQuestions();
      });
    });

    // Filter Chips
    els.filterChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        els.filterChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        state.currentFilterType = chip.dataset.type;
        renderQuestions();
      });
    });

    // Reset Data
    els.btnResetData.addEventListener('click', () => {
      if (confirm('确认清空所有做题记录、错题本与收藏数据？')) {
        state.userAnswers = {};
        state.starredIds.clear();
        state.wrongIds.clear();
        state.masteredIds.clear();
        saveLocalData();
        renderQuestions();
        updateStats();
        closeDrawer();
      }
    });

    // Diagram Toggle Events
    if (els.btnToggleDiagram) {
      els.btnToggleDiagram.addEventListener('click', toggleDiagram);
    }
    if (els.btnCloseDiagram) {
      els.btnCloseDiagram.addEventListener('click', closeDiagram);
    }

    // Random Exam Config Buttons
    els.examConfigBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        els.examConfigBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.examType = btn.dataset.examType;
        generateRandomExam();
      });
    });

    // Re-sample Random Exam
    if (els.btnReSample) {
      els.btnReSample.addEventListener('click', () => {
        generateRandomExam();
      });
    }

    // Submit Exam
    if (els.btnSubmitExam) {
      els.btnSubmitExam.addEventListener('click', () => {
        submitExam();
      });
    }

    // Close Score Modal
    if (els.btnCloseScore) {
      els.btnCloseScore.addEventListener('click', () => {
        els.examScoreModal.classList.add('hidden');
      });
    }

    // Review Exam Wrongs
    if (els.btnReviewExamWrongs) {
      els.btnReviewExamWrongs.addEventListener('click', () => {
        els.examScoreModal.classList.add('hidden');
        els.modeTabs.forEach((t) => t.classList.remove('active'));
        const wrongTab = document.querySelector('[data-mode="wrong"]');
        if (wrongTab) wrongTab.classList.add('active');
        state.currentMode = 'wrong';
        exitRandomExamMode();
        updateChapterView();
        renderQuestions();
      });
    }
  }

  // ================= RANDOM EXAM MODE =================
  function enterRandomExamMode() {
    if (els.randomExamPanel) els.randomExamPanel.classList.remove('hidden');
    if (els.chapterDescBanner) els.chapterDescBanner.classList.add('hidden');
    closeDiagram();
    generateRandomExam();
  }

  function exitRandomExamMode() {
    if (els.randomExamPanel) els.randomExamPanel.classList.add('hidden');
    if (els.chapterDescBanner) els.chapterDescBanner.classList.remove('hidden');
    stopExamTimer();
  }

  function startExamTimer() {
    stopExamTimer();
    state.examStartTime = Date.now();
    state.examTimerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - state.examStartTime) / 1000);
      const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
      const secs = String(elapsed % 60).padStart(2, '0');
      state.examDurationFormatted = `${mins}:${secs}`;
      if (els.examTimer) {
        els.examTimer.textContent = `⏱️ ${state.examDurationFormatted}`;
      }
    }, 1000);
  }

  function stopExamTimer() {
    if (state.examTimerInterval) {
      clearInterval(state.examTimerInterval);
      state.examTimerInterval = null;
    }
  }

  function generateRandomExam() {
    startExamTimer();
    state.examSubmitted = false;

    if (state.examType === 'rotation_18') {
      // 1 question per chapter for all 18 chapters
      const sampled = [];
      state.chapters.forEach((ch) => {
        const chQuestions = state.questions.filter((q) => q.chapterId === ch.id);
        if (chQuestions.length > 0) {
          const randIdx = Math.floor(Math.random() * chQuestions.length);
          sampled.push(chQuestions[randIdx]);
        }
      });
      state.randomQuestions = sampled;
    } else if (state.examType === 'random_30') {
      // Random 30 questions across all chapters
      const shuffled = [...state.questions].sort(() => 0.5 - Math.random());
      state.randomQuestions = shuffled.slice(0, Math.min(30, shuffled.length));
    } else if (state.examType === 'random_50') {
      // Random 50 questions across all chapters
      const shuffled = [...state.questions].sort(() => 0.5 - Math.random());
      state.randomQuestions = shuffled.slice(0, Math.min(50, shuffled.length));
    }

    renderQuestions();
    els.mainScroll.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function submitExam() {
    stopExamTimer();
    state.examSubmitted = true;

    const examList = state.randomQuestions;
    const totalCount = examList.length;
    let answeredCount = 0;
    let correctCount = 0;

    // Per chapter diagnostics map
    const chStats = {};

    examList.forEach((q) => {
      const chId = q.chapterId;
      if (!chStats[chId]) {
        chStats[chId] = { total: 0, correct: 0, wrong: 0, chTitle: '' };
        const chObj = state.chapters.find((c) => c.id === chId);
        chStats[chId].chTitle = chObj ? chObj.title : `第${chId}章`;
      }
      chStats[chId].total += 1;

      const ans = state.userAnswers[q.id];
      if (ans) {
        answeredCount++;
        if (ans.isCorrect) {
          correctCount++;
          chStats[chId].correct += 1;
        } else {
          chStats[chId].wrong += 1;
        }
      }
    });

    const accuracy = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

    // Populate Score Modal
    if (els.scorePercentage) els.scorePercentage.textContent = `${accuracy}%`;
    if (els.scoreAnswered) els.scoreAnswered.textContent = answeredCount;
    if (els.scoreTotal) els.scoreTotal.textContent = totalCount;
    if (els.scoreCorrect) els.scoreCorrect.textContent = correctCount;
    if (els.scoreDuration) els.scoreDuration.textContent = state.examDurationFormatted;

    // Populate Chapter Diagnostics
    if (els.chapterDiagnosticsList) {
      els.chapterDiagnosticsList.innerHTML = '';
      Object.keys(chStats).forEach((chId) => {
        const stat = chStats[chId];
        const chPct = stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0;
        let badgeColor = 'var(--success-color)';
        if (chPct < 60) badgeColor = 'var(--danger-color)';
        else if (chPct < 80) badgeColor = 'var(--warning-color)';

        const item = document.createElement('div');
        item.className = 'diagnostic-item';
        item.innerHTML = `
          <span class="diagnostic-name">${stat.chTitle}</span>
          <div class="diagnostic-bar-wrap">
            <div class="diagnostic-bar-fill" style="width: ${chPct}%; background: ${badgeColor};"></div>
          </div>
          <span class="diagnostic-badge" style="color: ${badgeColor};">${chPct}% (${stat.correct}/${stat.total})</span>
        `;
        els.chapterDiagnosticsList.appendChild(item);
      });
    }

    if (els.examScoreModal) {
      els.examScoreModal.classList.remove('hidden');
    }
  }

  // ================= DIAGRAMS =================
  function toggleDiagram() {
    if (!els.chapterDiagramBox) return;
    const isHidden = els.chapterDiagramBox.classList.contains('hidden');
    if (isHidden) {
      renderDiagram();
      els.chapterDiagramBox.classList.remove('hidden');
      if (els.btnToggleDiagram) {
        els.btnToggleDiagram.textContent = '📐 收起核心关系图解';
      }
    } else {
      closeDiagram();
    }
  }

  function closeDiagram() {
    if (!els.chapterDiagramBox) return;
    els.chapterDiagramBox.classList.add('hidden');
    if (els.btnToggleDiagram) {
      els.btnToggleDiagram.textContent = '📐 查看核心关系图解';
    }
  }

  function renderDiagram() {
    if (!els.diagramContent) return;
    const diagrams = (window.QUESTIONS_DATA && window.QUESTIONS_DATA.diagrams) || {};
    if (state.currentChapterId === 'all') {
      els.diagramContent.textContent = '【全部章节模式】\n请点击底部或右上角“目录 (18章)”，选择任意特定章节以查看该章节手写重构的核心关系图与知识图谱！';
    } else {
      const dText = diagrams[state.currentChapterId] || '暂无本章节关系图解';
      els.diagramContent.textContent = dText;
    }
  }

  // ================= DRAWER & VIEW =================
  function openDrawer() {
    renderDrawer();
    els.drawerOverlay.classList.remove('hidden');
  }

  function closeDrawer() {
    els.drawerOverlay.classList.add('hidden');
  }

  function renderDrawer() {
    els.drawerChapterList.innerHTML = '';

    // "All Chapters" item
    const allItem = document.createElement('div');
    allItem.className = `drawer-item ${state.currentChapterId === 'all' && state.currentMode !== 'random' ? 'active' : ''}`;
    allItem.innerHTML = `
      <span>🌟 全部章节 (综合全览)</span>
      <span class="drawer-item-count">${state.questions.length} 题</span>
    `;
    allItem.addEventListener('click', () => {
      if (state.currentMode === 'random') {
        els.modeTabs.forEach((t) => t.classList.remove('active'));
        const pTab = document.querySelector('[data-mode="practice"]');
        if (pTab) pTab.classList.add('active');
        state.currentMode = 'practice';
        exitRandomExamMode();
      }
      switchChapter('all');
      closeDrawer();
    });
    els.drawerChapterList.appendChild(allItem);

    // 18 Chapters
    state.chapters.forEach((ch) => {
      const chQuestions = state.questions.filter((q) => q.chapterId === ch.id);
      const answeredInCh = chQuestions.filter((q) => state.userAnswers[q.id]).length;

      const item = document.createElement('div');
      item.className = `drawer-item ${state.currentChapterId === ch.id && state.currentMode !== 'random' ? 'active' : ''}`;
      item.innerHTML = `
        <div style="flex: 1; min-width: 0; padding-right: 8px;">
          <div>${ch.title}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted);">${ch.desc}</div>
        </div>
        <span class="drawer-item-count">${answeredInCh}/${chQuestions.length}</span>
      `;
      item.addEventListener('click', () => {
        if (state.currentMode === 'random') {
          els.modeTabs.forEach((t) => t.classList.remove('active'));
          const pTab = document.querySelector('[data-mode="practice"]');
          if (pTab) pTab.classList.add('active');
          state.currentMode = 'practice';
          exitRandomExamMode();
        }
        switchChapter(ch.id);
        closeDrawer();
      });
      els.drawerChapterList.appendChild(item);
    });
  }

  function switchChapter(chId) {
    state.currentChapterId = chId;
    updateChapterView();
    if (els.chapterDiagramBox && !els.chapterDiagramBox.classList.contains('hidden')) {
      renderDiagram();
    }
    renderQuestions();
    els.mainScroll.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function updateChapterView() {
    if (state.currentMode === 'random') {
      els.currentChapterTitle.textContent = '🎲 全真随机抽题模考';
      els.currentChapterSubtitle.textContent = `当前模考集：${state.randomQuestions.length} 道题目`;
    } else if (state.currentChapterId === 'all') {
      els.currentChapterTitle.textContent = '全部章节 · 综合大题库';
      els.currentChapterSubtitle.textContent = `共 ${state.chapters.length} 章 · ${state.questions.length} 道精选题目`;
      els.chapterDescText.textContent = '全套知识点无缝打通，包含单选、判断、填空与高频必背简答大题。';
    } else {
      const ch = state.chapters.find((c) => c.id === state.currentChapterId);
      if (ch) {
        els.currentChapterTitle.textContent = ch.title;
        const chQuestions = state.questions.filter((q) => q.chapterId === ch.id);
        els.currentChapterSubtitle.textContent = `第 ${ch.id}/18 章 · 本章共 ${chQuestions.length} 题`;
        els.chapterDescText.textContent = ch.desc;
      }
    }
  }

  function getFilteredQuestions() {
    const sourceList = state.currentMode === 'random' ? state.randomQuestions : state.questions;

    return sourceList.filter((q) => {
      // Chapter filter (only if not in random mode)
      if (state.currentMode !== 'random') {
        if (state.currentChapterId !== 'all' && q.chapterId !== state.currentChapterId) {
          return false;
        }
      }

      // Mode filter
      if (state.currentMode === 'wrong' && !state.wrongIds.has(q.id)) {
        return false;
      }
      if (state.currentMode === 'star' && !state.starredIds.has(q.id)) {
        return false;
      }

      // Type filter
      if (state.currentFilterType !== 'all' && q.type !== state.currentFilterType) {
        return false;
      }

      // Search query
      if (state.searchQuery) {
        const matchTitle = q.title.toLowerCase().includes(state.searchQuery);
        const matchAns = (q.answer || '').toLowerCase().includes(state.searchQuery);
        const matchExp = (q.explanation || '').toLowerCase().includes(state.searchQuery);
        const matchTag = (q.examTag || '').toLowerCase().includes(state.searchQuery);
        if (!matchTitle && !matchAns && !matchExp && !matchTag) return false;
      }

      return true;
    });
  }

  function renderQuestions() {
    const filtered = getFilteredQuestions();

    updateCounts();

    if (filtered.length === 0) {
      els.questionsContainer.innerHTML = '';
      els.emptyState.classList.remove('hidden');
      return;
    }

    els.emptyState.classList.add('hidden');
    els.questionsContainer.innerHTML = '';

    filtered.forEach((q, index) => {
      const card = createQuestionCard(q, index + 1);
      els.questionsContainer.appendChild(card);
    });
  }

  function updateCounts() {
    const sourceList = state.currentMode === 'random' ? state.randomQuestions : state.questions;
    const baseList = sourceList.filter((q) => {
      if (state.currentMode !== 'random' && state.currentChapterId !== 'all' && q.chapterId !== state.currentChapterId) return false;
      if (state.currentMode === 'wrong' && !state.wrongIds.has(q.id)) return false;
      if (state.currentMode === 'star' && !state.starredIds.has(q.id)) return false;
      return true;
    });

    els.totalTypeCount.textContent = baseList.length;
    els.choiceTypeCount.textContent = baseList.filter((q) => q.type === 'choice').length;
    if (els.judgeTypeCount) {
      els.judgeTypeCount.textContent = baseList.filter((q) => q.type === 'judge').length;
    }
    els.blankTypeCount.textContent = baseList.filter((q) => q.type === 'blank').length;
    els.shortTypeCount.textContent = baseList.filter((q) => q.type === 'short').length;

    els.wrongCount.textContent = state.wrongIds.size;
    els.starCount.textContent = state.starredIds.size;
  }

  // ================= CARD FACTORY =================
  function createQuestionCard(q, displayNum) {
    const card = document.createElement('div');
    card.className = 'question-card';
    card.id = `card-${q.id}`;

    const isStarred = state.starredIds.has(q.id);
    const userAnswer = state.userAnswers[q.id];
    const isReciteMode = state.currentMode === 'recite';
    const isRevealed = isReciteMode || state.revealedCardIds.has(q.id);

    const typeNames = { choice: '单选题', judge: '判断题', blank: '填空题', short: '简答题' };

    // Header HTML
    const headerHtml = `
      <div class="card-header">
        <div class="card-tags">
          <span class="type-tag ${q.type}">${typeNames[q.type] || '题目'}</span>
          ${q.examTag ? `<span class="exam-tag">${q.examTag}</span>` : ''}
          <span style="font-size: 0.72rem; color: var(--text-muted);">#${displayNum}</span>
        </div>
        <button class="star-btn ${isStarred ? 'starred' : ''}" data-id="${q.id}" aria-label="收藏题目">
          ${isStarred ? '★' : '☆'}
        </button>
      </div>
    `;

    // Title HTML
    let titleHtml = `<div class="question-title">${q.title}</div>`;
    if (q.type === 'blank') {
      if (isRevealed) {
        const highlightedTitle = q.title.replace(/【([^】]+)】/g, '<span style="color:var(--success-color); font-weight:700; text-decoration:underline;">$1</span>');
        titleHtml = `<div class="question-title">${highlightedTitle}</div>`;
      } else {
        const maskedTitle = q.title.replace(/【([^】]+)】/g, '<span style="border-bottom:2px dashed var(--accent-color); padding: 0 10px; color:transparent; background:var(--accent-light); border-radius:3px;">____</span>');
        titleHtml = `<div class="question-title">${maskedTitle}</div>`;
      }
    }

    let bodyHtml = '';

    // 1. Multiple Choice
    if (q.type === 'choice') {
      bodyHtml = `
        <div class="options-list">
          ${q.options.map((opt) => {
            const optKey = opt.trim().charAt(0).toUpperCase();
            let optClass = 'option-btn';

            if (userAnswer) {
              if (optKey === q.answer) {
                optClass += ' show-correct';
              }
              if (userAnswer.selectedOption === optKey) {
                if (userAnswer.isCorrect) {
                  optClass += ' selected-correct';
                } else {
                  optClass += ' selected-wrong';
                }
              }
            } else if (isReciteMode) {
              if (optKey === q.answer) {
                optClass += ' show-correct';
              }
            }

            return `
              <button class="${optClass}" data-qid="${q.id}" data-opt="${optKey}" ${userAnswer && !isReciteMode ? 'disabled' : ''}>
                ${opt}
              </button>
            `;
          }).join('')}
        </div>
      `;

      if (userAnswer || isRevealed) {
        bodyHtml += `
          <div class="explanation-box">
            <div class="explanation-title">
              <span>💡 正确答案: <b>${q.answer}</b></span>
            </div>
            <div class="explanation-text">${q.explanation || '暂无详细解析'}</div>
          </div>
        `;

        if (q.trapOption && q.trapAnalysis) {
          bodyHtml += `
            <div class="trap-box">
              <div class="trap-header">
                <span>🎯【教授易错陷阱剖析】</span>
              </div>
              <div class="trap-text">
                <div style="font-weight:700; color:var(--danger-color); margin-bottom:4px;">⚠️ 易错高危混淆项：${q.trapOption}</div>
                <div>${q.trapAnalysis}</div>
              </div>
            </div>
          `;
        }
      }
    }
    // 2. True / False (Judge)
    else if (q.type === 'judge') {
      let trueClass = 'judge-btn';
      let falseClass = 'judge-btn';

      if (userAnswer) {
        if (q.answer === '正确') trueClass += ' show-correct';
        if (q.answer === '错误') falseClass += ' show-correct';

        if (userAnswer.selectedOption === '正确') {
          trueClass += userAnswer.isCorrect ? ' selected-correct' : ' selected-wrong';
        } else if (userAnswer.selectedOption === '错误') {
          falseClass += userAnswer.isCorrect ? ' selected-correct' : ' selected-wrong';
        }
      } else if (isReciteMode) {
        if (q.answer === '正确') trueClass += ' show-correct';
        if (q.answer === '错误') falseClass += ' show-correct';
      }

      bodyHtml = `
        <div class="judge-options-row">
          <button class="${trueClass}" data-qid="${q.id}" data-judge="正确" ${userAnswer && !isReciteMode ? 'disabled' : ''}>
            ✓ 正确
          </button>
          <button class="${falseClass}" data-qid="${q.id}" data-judge="错误" ${userAnswer && !isReciteMode ? 'disabled' : ''}>
            ✕ 错误
          </button>
        </div>
      `;

      if (userAnswer || isRevealed) {
        bodyHtml += `
          <div class="explanation-box">
            <div class="explanation-title">
              <span>💡 正确判断: <b>${q.answer}</b></span>
            </div>
            <div class="explanation-text">${q.explanation || '暂无详细解析'}</div>
          </div>
        `;

        if (q.trapOption && q.trapAnalysis) {
          bodyHtml += `
            <div class="trap-box">
              <div class="trap-header">
                <span>🎯【教授易错考点透视】</span>
              </div>
              <div class="trap-text">
                <div style="font-weight:700; color:var(--danger-color); margin-bottom:4px;">⚠️ 核心概念误区：${q.trapOption}</div>
                <div>${q.trapAnalysis}</div>
              </div>
            </div>
          `;
        }
      }
    }
    // 3. Fill-in-the-blank
    else if (q.type === 'blank') {
      if (isRevealed) {
        bodyHtml = `
          <div class="blank-card-answer">
            <span>✨ 参考填空: <b>${q.answer}</b></span>
          </div>
          ${q.explanation ? `<div class="explanation-box"><div class="explanation-text">${q.explanation}</div></div>` : ''}
          <button class="toggle-answer-btn" data-toggle="${q.id}">隐藏填空答案</button>
        `;
      } else {
        bodyHtml = `
          <button class="toggle-answer-btn" data-toggle="${q.id}">🔍 点击查看填空答案</button>
        `;
      }
    }
    // 4. Short Answer / Essay
    else if (q.type === 'short') {
      const isMastered = state.masteredIds.has(q.id);

      if (isRevealed) {
        bodyHtml = `
          <div class="explanation-box" style="margin-top: 6px;">
            <div class="explanation-title">🎯 核心得分点速记清单</div>
            <div class="points-list">
              ${(q.points || []).map((pt, i) => `
                <div class="point-item">
                  <span style="font-weight:700; color:var(--accent-color);">${i + 1}.</span>
                  <span>${pt}</span>
                </div>
              `).join('')}
            </div>
            <div style="margin-top: 10px; font-weight:700; color:var(--text-primary); font-size:0.85rem;">📝 完整标准答案:</div>
            <div class="explanation-text" style="margin-top: 4px;">${q.answer}</div>
          </div>
          <div class="mastery-row">
            <button class="mastery-btn ${isMastered ? 'active-mastered' : ''}" data-mastery="${q.id}" data-val="yes">
              ${isMastered ? '✓ 已牢记' : '标记已牢记'}
            </button>
            <button class="mastery-btn ${!isMastered && state.wrongIds.has(q.id) ? 'active-review' : ''}" data-mastery="${q.id}" data-val="no">
              加入强化复习
            </button>
          </div>
          <button class="toggle-answer-btn" data-toggle="${q.id}" style="margin-top: 10px;">收起得分点解析</button>
        `;
      } else {
        bodyHtml = `
          <button class="toggle-answer-btn" data-toggle="${q.id}">📖 展开核心得分点与参考答案</button>
        `;
      }
    }

    card.innerHTML = headerHtml + titleHtml + bodyHtml;

    // Attach card event listeners
    const starBtn = card.querySelector('.star-btn');
    if (starBtn) {
      starBtn.addEventListener('click', () => toggleStar(q.id));
    }

    const optBtns = card.querySelectorAll('.option-btn');
    optBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        handleChoiceClick(btn.dataset.qid, btn.dataset.opt);
      });
    });

    const judgeBtns = card.querySelectorAll('.judge-btn');
    judgeBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        handleJudgeClick(btn.dataset.qid, btn.dataset.judge);
      });
    });

    const toggleBtn = card.querySelector('[data-toggle]');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => toggleCardReveal(q.id));
    }

    const masteryBtns = card.querySelectorAll('[data-mastery]');
    masteryBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        handleMasteryClick(btn.dataset.mastery, btn.dataset.val === 'yes');
      });
    });

    return card;
  }

  // ================= ACTION HANDLERS =================
  function handleChoiceClick(qId, selectedOption) {
    const q = state.questions.find((item) => item.id === qId);
    if (!q) return;

    const isCorrect = selectedOption === q.answer;
    state.userAnswers[qId] = { selectedOption, isCorrect, timestamp: Date.now() };

    if (!isCorrect) {
      state.wrongIds.add(qId);
      if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
    } else {
      if (state.wrongIds.has(qId)) {
        state.wrongIds.delete(qId);
      }
      if (navigator.vibrate) navigator.vibrate(25);
    }

    saveLocalData();
    updateStats();

    const cardEl = document.getElementById(`card-${qId}`);
    if (cardEl) {
      const num = cardEl.querySelector('.card-tags span:last-child')?.textContent?.replace('#', '') || '1';
      const newCard = createQuestionCard(q, num);
      cardEl.replaceWith(newCard);
    }
  }

  function handleJudgeClick(qId, selectedVal) {
    const q = state.questions.find((item) => item.id === qId);
    if (!q) return;

    const isCorrect = selectedVal === q.answer;
    state.userAnswers[qId] = { selectedOption: selectedVal, isCorrect, timestamp: Date.now() };

    if (!isCorrect) {
      state.wrongIds.add(qId);
      if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
    } else {
      if (state.wrongIds.has(qId)) {
        state.wrongIds.delete(qId);
      }
      if (navigator.vibrate) navigator.vibrate(25);
    }

    saveLocalData();
    updateStats();

    const cardEl = document.getElementById(`card-${qId}`);
    if (cardEl) {
      const num = cardEl.querySelector('.card-tags span:last-child')?.textContent?.replace('#', '') || '1';
      const newCard = createQuestionCard(q, num);
      cardEl.replaceWith(newCard);
    }
  }

  function toggleStar(qId) {
    if (state.starredIds.has(qId)) {
      state.starredIds.delete(qId);
    } else {
      state.starredIds.add(qId);
      if (navigator.vibrate) navigator.vibrate(20);
    }
    saveLocalData();
    updateCounts();

    const starBtn = document.querySelector(`#card-${qId} .star-btn`);
    if (starBtn) {
      starBtn.classList.toggle('starred', state.starredIds.has(qId));
      starBtn.textContent = state.starredIds.has(qId) ? '★' : '☆';
    }
  }

  function toggleCardReveal(qId) {
    if (state.revealedCardIds.has(qId)) {
      state.revealedCardIds.delete(qId);
    } else {
      state.revealedCardIds.add(qId);
    }

    const q = state.questions.find((item) => item.id === qId);
    if (q) {
      const cardEl = document.getElementById(`card-${qId}`);
      if (cardEl) {
        const num = cardEl.querySelector('.card-tags span:last-child')?.textContent?.replace('#', '') || '1';
        const newCard = createQuestionCard(q, num);
        cardEl.replaceWith(newCard);
      }
    }
  }

  function handleMasteryClick(qId, isMastered) {
    if (isMastered) {
      state.masteredIds.add(qId);
      state.wrongIds.delete(qId);
    } else {
      state.masteredIds.delete(qId);
      state.wrongIds.add(qId);
    }
    saveLocalData();
    updateCounts();

    const q = state.questions.find((item) => item.id === qId);
    if (q) {
      const cardEl = document.getElementById(`card-${qId}`);
      if (cardEl) {
        const num = cardEl.querySelector('.card-tags span:last-child')?.textContent?.replace('#', '') || '1';
        const newCard = createQuestionCard(q, num);
        cardEl.replaceWith(newCard);
      }
    }
  }

  function updateStats() {
    const totalQuestions = state.questions.length;
    const answeredCount = Object.keys(state.userAnswers).length;
    let correctCount = 0;

    Object.values(state.userAnswers).forEach((ans) => {
      if (ans.isCorrect) correctCount++;
    });

    const accuracy = answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0;
    const progressPercent = totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0;

    els.statAnswered.textContent = answeredCount;
    els.statTotal.textContent = totalQuestions;
    els.statAccuracy.textContent = `${accuracy}%`;
    els.progressFill.style.width = `${progressPercent}%`;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
'''

with open("/Volumes/Ext/dev/python/pdf_compressor/web/app.js", "w", encoding="utf-8") as f:
    f.write(app_js_code)

print("Successfully written clean full app.js!")
