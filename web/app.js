/**
 * 心理学导论 · 全章节刷题、模考与抽背系统 (347备考)
 * Client Application Logic (Final Complete Version)
 * - 刷题练习模式：单选题、判断题、填空题交互输入核对、简答题草稿与得分点自评
 * - 全真随机模考：18章轮转模考、30题冲刺、50题综合，动态计时，交卷前不剧透答案，提交后出具各章节薄弱点报告
 * - 考点抽背闪卡模式：纯净“概念/问题-答案（点击显示）”，完全源自原书与笔记，支持点击翻看与“🎲 随机抽背一题”
 * - 错题本：无剧透盲测重练，答对即刻提供“移出错题本”
 * - 多端云同步：基于 Cloudflare KV，支持密码＋专属授权码双重认证，未登录可纯离线使用
 */

(function () {
  'use strict';

  // State
  const state = {
    chapters: [],
    questions: [],
    recitations: [], // 纯净抽背闪卡数据 (概念/问题 - 答案)
    currentChapterId: 1, // 1 to 18, or 'all'
    currentMode: 'practice', // 'practice', 'random', 'recite', 'wrong', 'star'
    currentFilterType: 'all', // 'all', 'choice', 'judge', 'blank', 'short'
    reciteFilter: 'all', // 'all', 'essay', 'noun', 'review'
    searchQuery: '',
    theme: 'light',

    // User Progress Data
    userAnswers: {}, // { qId: { selectedOption, isCorrect, timestamp, userText, score, checkedPoints } }
    starredIds: new Set(),
    wrongIds: new Set(),
    revealedCardIds: new Set(),
    masteredIds: new Set(),

    // Recitation Status Data
    reciteStatus: {}, // { recId: 'mastered' | 'review' }
    reciteRevealedIds: new Set(),

    // Session Answers (独立重测状态，杜绝剧透高亮)
    wrongRetestAnswers: {}, // 错题本当前轮次的即时作答
    examSessionAnswers: {}, // 模考当前轮次的即时作答

    // Cloud Sync State (Cloudflare KV)
    user: {
      username: '',
      password: '',
      authCode: '',
      lastSyncTime: 0,
    },
    isSyncing: false,

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
    btnResetChapter: document.getElementById('btn-reset-chapter'),
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
    filterRow: document.querySelector('.filter-row'),
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

    // Recitation Toolbar Elements
    recitationToolbar: document.getElementById('recitation-toolbar'),
    btnRandomRecite: document.getElementById('btn-random-recite'),
    reciteChips: document.querySelectorAll('.recite-chip'),
    reciteAllCount: document.getElementById('recite-all-count'),
    reciteEssayCount: document.getElementById('recite-essay-count'),
    reciteNounCount: document.getElementById('recite-noun-count'),
    reciteReviewCount: document.getElementById('recite-review-count'),
    btnExpandAllRecite: document.getElementById('btn-expand-all-recite'),
    btnCollapseAllRecite: document.getElementById('btn-collapse-all-recite'),

    // Cloud Sync Elements
    btnSyncToggle: document.getElementById('btn-sync-toggle'),
    syncStatusText: document.getElementById('sync-status-text'),
    syncModal: document.getElementById('sync-modal'),
    btnCloseSync: document.getElementById('btn-close-sync'),
    syncUserStatus: document.getElementById('sync-user-status'),
    syncLastTime: document.getElementById('sync-last-time'),
    syncFormArea: document.getElementById('sync-form-area'),
    syncLoggedArea: document.getElementById('sync-logged-area'),
    syncUsernameInput: document.getElementById('sync-username-input'),
    syncPasswordInput: document.getElementById('sync-password-input'),
    syncAuthcodeInput: document.getElementById('sync-authcode-input'),
    btnDoLogin: document.getElementById('btn-do-login'),
    btnDoManualSync: document.getElementById('btn-do-manual-sync'),
    btnDoLogout: document.getElementById('btn-do-logout'),
  };

  // Local Storage Keys
  const STORAGE_KEYS = {
    THEME: 'psych_theme_pref',
    ANSWERS: 'psych_answers_data',
    STARS: 'psych_stars_data',
    WRONGS: 'psych_wrongs_data',
    MASTERED: 'psych_mastered_data',
    RECITE_STATUS: 'psych_recite_status',
    USER: 'psych_user_auth',
  };

  function init() {
    loadLocalData();
    initTheme();
    updateSyncButtonState();
    bindEvents();

    if (window.QUESTIONS_DATA) {
      state.chapters = window.QUESTIONS_DATA.chapters || [];
      state.questions = window.QUESTIONS_DATA.questions || [];
      state.recitations = window.QUESTIONS_DATA.recitations || [];
    }

    renderDrawer();
    updateChapterView();
    renderQuestions();
    updateStats();

    if (state.user && state.user.username) {
      setTimeout(() => syncWithCloud(false), 1000);
    }
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

      const savedRecite = localStorage.getItem(STORAGE_KEYS.RECITE_STATUS);
      if (savedRecite) state.reciteStatus = JSON.parse(savedRecite);

      const savedUser = localStorage.getItem(STORAGE_KEYS.USER);
      if (savedUser) state.user = JSON.parse(savedUser);
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
      localStorage.setItem(STORAGE_KEYS.RECITE_STATUS, JSON.stringify(state.reciteStatus));
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state.user));
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

  // ================= CLOUD SYNC LOGIC =================
  function updateSyncButtonState() {
    if (!els.syncStatusText) return;
    if (state.user && state.user.username) {
      els.syncStatusText.textContent = state.user.username;
      els.btnSyncToggle.classList.add('synced');
    } else {
      els.syncStatusText.textContent = '本地';
      els.btnSyncToggle.classList.remove('synced');
    }
  }

  function openSyncModal() {
    if (!els.syncModal) return;
    const isLogged = !!(state.user && state.user.username);

    if (isLogged) {
      els.syncUserStatus.textContent = `已连接账号: ${state.user.username}`;
      const lastTimeStr = state.user.lastSyncTime ? new Date(state.user.lastSyncTime).toLocaleString() : '刚刚';
      els.syncLastTime.textContent = `上次云同步时间: ${lastTimeStr}`;
      els.syncFormArea.classList.add('hidden');
      els.syncLoggedArea.classList.remove('hidden');
    } else {
      els.syncUserStatus.textContent = '当前状态: 本地离线模式';
      els.syncLastTime.textContent = '刷题记录与进度仅保存在当前设备浏览器中';
      els.syncFormArea.classList.remove('hidden');
      els.syncLoggedArea.classList.add('hidden');
      if (els.syncUsernameInput) els.syncUsernameInput.value = '';
      if (els.syncPasswordInput) els.syncPasswordInput.value = '';
      if (els.syncAuthcodeInput) els.syncAuthcodeInput.value = state.user.authCode || '';
    }

    els.syncModal.classList.remove('hidden');
  }

  function closeSyncModal() {
    if (els.syncModal) els.syncModal.classList.add('hidden');
  }

  let syncDebounceTimer = null;
  function triggerAutoSync() {
    if (!state.user || !state.user.username) return;
    if (syncDebounceTimer) clearTimeout(syncDebounceTimer);
    syncDebounceTimer = setTimeout(() => {
      syncWithCloud(false);
    }, 2000);
  }

  async function syncWithCloud(showAlert = true) {
    if (!state.user || !state.user.username) return;
    if (state.isSyncing) return;
    state.isSyncing = true;
    if (els.syncStatusText) els.syncStatusText.textContent = '同步中...';

    const clientPayload = {
      answers: state.userAnswers,
      stars: Array.from(state.starredIds),
      wrongs: Array.from(state.wrongIds),
      mastered: Array.from(state.masteredIds),
      reciteStatus: state.reciteStatus,
    };

    try {
      const resp = await fetch('/api/user/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: state.user.username,
          password: state.user.password,
          authCode: state.user.authCode || '',
          payload: clientPayload,
        }),
      });

      const res = await resp.json();

      if (!resp.ok || !res.success) {
        throw new Error(res.message || '同步请求失败');
      }

      const cloudPayload = res.payload || {};
      state.userAnswers = cloudPayload.answers || state.userAnswers;
      state.starredIds = new Set(cloudPayload.stars || []);
      state.wrongIds = new Set(cloudPayload.wrongs || []);
      state.masteredIds = new Set(cloudPayload.mastered || []);
      if (cloudPayload.reciteStatus) {
        state.reciteStatus = { ...state.reciteStatus, ...cloudPayload.reciteStatus };
      }
      state.user.lastSyncTime = res.updatedAt || Date.now();

      saveLocalData();
      updateSyncButtonState();
      updateStats();
      renderQuestions();

      if (showAlert) {
        alert(`☁️ 同步成功！\n${res.message}\n已同步 ${Object.keys(state.userAnswers).length} 道答题记录与背诵进度`);
        closeSyncModal();
      }
    } catch (err) {
      console.warn('Sync failed:', err);
      if (showAlert) {
        alert('同步失败: ' + err.message);
      }
      updateSyncButtonState();
    } finally {
      state.isSyncing = false;
    }
  }

  async function handleLoginSync() {
    const username = (els.syncUsernameInput.value || '').trim();
    const password = (els.syncPasswordInput.value || '').trim();
    const authCode = (els.syncAuthcodeInput ? els.syncAuthcodeInput.value : '').trim();

    if (!username) {
      alert('请输入同步用户名');
      return;
    }
    if (!authCode && !(state.user && state.user.authCode)) {
      alert('请输入管理员分发的专属授权认证码（首次绑定多端同步必须提供，如向管理员索取）');
      return;
    }

    state.user = {
      username: username,
      password: password,
      authCode: authCode || (state.user && state.user.authCode) || '',
      lastSyncTime: 0,
    };

    await syncWithCloud(true);
  }

  function handleLogout() {
    if (confirm('确认退出登录并切回本地离线模式？本地数据不会被清除。')) {
      state.user = { username: '', password: '', authCode: '', lastSyncTime: 0 };
      saveLocalData();
      updateSyncButtonState();
      closeSyncModal();
      alert('已切换回本地模式');
    }
  }

  function bindEvents() {
    els.btnTheme.addEventListener('click', toggleTheme);

    if (els.btnSyncToggle) els.btnSyncToggle.addEventListener('click', openSyncModal);
    if (els.btnCloseSync) els.btnCloseSync.addEventListener('click', closeSyncModal);
    if (els.btnDoLogin) els.btnDoLogin.addEventListener('click', handleLoginSync);
    if (els.btnDoManualSync) els.btnDoManualSync.addEventListener('click', () => syncWithCloud(true));
    if (els.btnDoLogout) els.btnDoLogout.addEventListener('click', handleLogout);

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
      if (e.target === els.syncModal) closeSyncModal();
      if (e.target === els.examScoreModal) els.examScoreModal.classList.add('hidden');
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

    // Mode Tabs Switching
    els.modeTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        els.modeTabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        state.currentMode = tab.dataset.mode;

        if (state.currentMode === 'random') {
          enterRandomExamMode();
        } else if (state.currentMode === 'wrong') {
          state.wrongRetestAnswers = {};
          exitRandomExamMode();
        } else {
          exitRandomExamMode();
        }

        updateChapterView();
        renderQuestions();
      });
    });

    // Practice Filter Chips
    els.filterChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        els.filterChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        state.currentFilterType = chip.dataset.type;
        renderQuestions();
      });
    });

    // Recite Filter Chips
    els.reciteChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        els.reciteChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        state.reciteFilter = chip.dataset.reciteFilter;
        renderQuestions();
      });
    });

    // Random Oral Flashcard Draw (🎲 随机抽背一题)
    if (els.btnRandomRecite) {
      els.btnRandomRecite.addEventListener('click', () => {
        handleRandomReciteDraw();
      });
    }

    // Expand / Collapse all recitation cards
    if (els.btnExpandAllRecite) {
      els.btnExpandAllRecite.addEventListener('click', () => {
        const filtered = getFilteredRecitations();
        filtered.forEach((r) => state.reciteRevealedIds.add(r.id));
        renderQuestions();
      });
    }
    if (els.btnCollapseAllRecite) {
      els.btnCollapseAllRecite.addEventListener('click', () => {
        state.reciteRevealedIds.clear();
        renderQuestions();
      });
    }

    // Reset Data
    els.btnResetData.addEventListener('click', () => {
      if (confirm('确认清空所有做题记录、错题本与收藏数据？')) {
        state.userAnswers = {};
        state.starredIds.clear();
        state.wrongIds.clear();
        state.masteredIds.clear();
        state.reciteStatus = {};
        state.wrongRetestAnswers = {};
        state.examSessionAnswers = {};
        saveLocalData();
        renderQuestions();
        updateStats();
        closeDrawer();
        triggerAutoSync();
      }
    });

    // Reset Current Chapter Answers Event
    if (els.btnResetChapter) {
      els.btnResetChapter.addEventListener('click', resetCurrentChapterAnswers);
    }

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
        state.wrongRetestAnswers = {};
        exitRandomExamMode();
        updateChapterView();
        renderQuestions();
      });
    }
  }

  // ================= CHAPTER LEVEL RESET =================
  function resetCurrentChapterAnswers() {
    if (state.currentChapterId === 'all') {
      if (!confirm('确认清空全书所有题目的作答记录，重新开始自测？')) return;
      state.userAnswers = {};
    } else {
      const ch = state.chapters.find((c) => c.id === state.currentChapterId);
      const chName = ch ? ch.title : `第${state.currentChapterId}章`;
      if (!confirm(`确认清空【${chName}】的所有作答记录，重新开始自测？`)) return;
      const chQuestions = state.questions.filter((q) => q.chapterId === state.currentChapterId);
      chQuestions.forEach((q) => {
        delete state.userAnswers[q.id];
      });
    }
    saveLocalData();
    updateStats();
    renderQuestions();
    triggerAutoSync();
  }

  // ================= RANDOM EXAM MODE =================
  function enterRandomExamMode() {
    if (els.randomExamPanel) els.randomExamPanel.classList.remove('hidden');
    if (els.chapterDescBanner) els.chapterDescBanner.classList.add('hidden');
    if (els.recitationToolbar) els.recitationToolbar.classList.add('hidden');
    if (els.filterRow) els.filterRow.classList.remove('hidden');
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
    state.examSessionAnswers = {};

    if (state.examType === 'rotation_18') {
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
      const shuffled = [...state.questions].sort(() => 0.5 - Math.random());
      state.randomQuestions = shuffled.slice(0, Math.min(30, shuffled.length));
    } else if (state.examType === 'random_50') {
      const shuffled = [...state.questions].sort(() => 0.5 - Math.random());
      state.randomQuestions = shuffled.slice(0, Math.min(50, shuffled.length));
    }

    renderQuestions();
    els.mainScroll.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function submitExam() {
    stopExamTimer();
    state.examSubmitted = true;

    state.randomQuestions.forEach((q) => {
      if (q.type === 'blank') {
        const inputEl = document.getElementById(`blank-input-${q.id}`);
        if (inputEl && inputEl.value.trim() && !state.examSessionAnswers[q.id]) {
          evaluateBlankAnswer(q.id, inputEl.value.trim());
        }
      }
    });

    const examList = state.randomQuestions;
    const totalCount = examList.length;
    let answeredCount = 0;
    let correctCount = 0;

    const chStats = {};

    examList.forEach((q) => {
      const chId = q.chapterId;
      if (!chStats[chId]) {
        chStats[chId] = { total: 0, correct: 0, wrong: 0, chTitle: '' };
        const chObj = state.chapters.find((c) => c.id === chId);
        chStats[chId].chTitle = chObj ? chObj.title : `第${chId}章`;
      }
      chStats[chId].total += 1;

      const ans = state.examSessionAnswers[q.id];
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

    if (els.scorePercentage) els.scorePercentage.textContent = `${accuracy}%`;
    if (els.scoreAnswered) els.scoreAnswered.textContent = answeredCount;
    if (els.scoreTotal) els.scoreTotal.textContent = totalCount;
    if (els.scoreCorrect) els.scoreCorrect.textContent = correctCount;
    if (els.scoreDuration) els.scoreDuration.textContent = state.examDurationFormatted;

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

    renderQuestions();
    triggerAutoSync();
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

    const allItem = document.createElement('div');
    allItem.className = `drawer-item ${state.currentChapterId === 'all' && state.currentMode !== 'random' ? 'active' : ''}`;
    allItem.innerHTML = `
      <span>🌟 全部章节 (综合全览)</span>
      <span class="drawer-item-count">${state.questions.length} 题 / ${state.recitations.length} 闪卡</span>
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

    state.chapters.forEach((ch) => {
      const chQuestions = state.questions.filter((q) => q.chapterId === ch.id);
      const chRecitations = state.recitations.filter((r) => r.chapterId === ch.id);
      const answeredInCh = chQuestions.filter((q) => state.userAnswers[q.id]).length;

      const item = document.createElement('div');
      item.className = `drawer-item ${state.currentChapterId === ch.id && state.currentMode !== 'random' ? 'active' : ''}`;
      item.innerHTML = `
        <div style="flex: 1; min-width: 0; padding-right: 8px;">
          <div>${ch.title}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted);">${ch.desc}</div>
        </div>
        <span class="drawer-item-count">${answeredInCh}/${chQuestions.length} (${chRecitations.length}闪卡)</span>
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
    } else if (state.currentMode === 'recite') {
      const ch = state.chapters.find((c) => c.id === state.currentChapterId);
      if (state.currentChapterId === 'all') {
        els.currentChapterTitle.textContent = '📖 考研考点抽背 (全部章节)';
        els.currentChapterSubtitle.textContent = `全书共 ${state.recitations.length} 张核心考点抽背闪卡`;
      } else if (ch) {
        els.currentChapterTitle.textContent = `📖 考点抽背 · ${ch.title}`;
        const chReciteCount = state.recitations.filter((r) => r.chapterId === ch.id).length;
        els.currentChapterSubtitle.textContent = `本章共 ${chReciteCount} 张核心概念与简答闪卡`;
      }
      els.chapterDescText.textContent = '【纯净抽背闪卡模式】完全源自原书与笔记原文；默认隐藏答案，点击卡片即可翻看踩点清单，专供师生/研友面对面抽背！';
    } else if (state.currentMode === 'wrong') {
      els.currentChapterTitle.textContent = '❌ 错题专项攻坚本';
      els.currentChapterSubtitle.textContent = `待攻克错题：${state.wrongIds.size} 道`;
      els.chapterDescText.textContent = '【无剧透盲测重练】错题默认以未作答状态呈现，绝无预先高亮剧透。重新作答正确后，可一键将其移出错题本！';
    } else if (state.currentChapterId === 'all') {
      els.currentChapterTitle.textContent = '全部章节 · 综合大题库';
      els.currentChapterSubtitle.textContent = `共 ${state.chapters.length} 章 · ${state.questions.length} 道精选题`;
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

  // ================= MAIN RENDER DISPATCHER =================
  function renderQuestions() {
    if (state.currentMode === 'recite') {
      // Show recitation toolbar, hide standard filter row
      if (els.recitationToolbar) els.recitationToolbar.classList.remove('hidden');
      if (els.filterRow) els.filterRow.classList.add('hidden');
      renderRecitationFlashcards();
    } else {
      // Non-recite modes: show standard filter row, hide recitation toolbar
      if (els.recitationToolbar) els.recitationToolbar.classList.add('hidden');
      if (els.filterRow) els.filterRow.classList.remove('hidden');
      renderQuizCards();
    }
  }

  // ================= 1. RECITATION FLASHCARDS RENDERER =================
  function getFilteredRecitations() {
    return state.recitations.filter((r) => {
      // Chapter filter
      if (state.currentChapterId !== 'all' && r.chapterId !== state.currentChapterId) {
        return false;
      }

      // Recite Category filter
      if (state.reciteFilter === 'essay') {
        if (r.category !== '简答大题' && r.category !== '核心理论') return false;
      } else if (state.reciteFilter === 'noun') {
        if (r.category !== '名词解释' && r.category !== '概念辨析') return false;
      } else if (state.reciteFilter === 'review') {
        if (state.reciteStatus[r.id] !== 'review') return false;
      }

      // Search query
      if (state.searchQuery) {
        const matchTitle = (r.title || '').toLowerCase().includes(state.searchQuery);
        const matchAns = (r.answer || '').toLowerCase().includes(state.searchQuery);
        const matchTag = (r.sourceTag || '').toLowerCase().includes(state.searchQuery);
        const matchPoints = (r.points || []).some((pt) => pt.toLowerCase().includes(state.searchQuery));
        if (!matchTitle && !matchAns && !matchTag && !matchPoints) return false;
      }

      return true;
    });
  }

  function renderRecitationFlashcards() {
    const list = getFilteredRecitations();
    updateRecitationCounts();

    if (list.length === 0) {
      els.questionsContainer.innerHTML = '';
      els.emptyState.classList.remove('hidden');
      return;
    }

    els.emptyState.classList.add('hidden');
    els.questionsContainer.innerHTML = '';

    list.forEach((r, index) => {
      const card = createFlashcardElement(r, index + 1);
      els.questionsContainer.appendChild(card);
    });
  }

  function updateRecitationCounts() {
    const baseList = state.recitations.filter((r) => {
      if (state.currentChapterId !== 'all' && r.chapterId !== state.currentChapterId) return false;
      return true;
    });

    if (els.reciteAllCount) els.reciteAllCount.textContent = baseList.length;
    if (els.reciteEssayCount) {
      els.reciteEssayCount.textContent = baseList.filter((r) => r.category === '简答大题' || r.category === '核心理论').length;
    }
    if (els.reciteNounCount) {
      els.reciteNounCount.textContent = baseList.filter((r) => r.category === '名词解释' || r.category === '概念辨析').length;
    }
    if (els.reciteReviewCount) {
      els.reciteReviewCount.textContent = baseList.filter((r) => state.reciteStatus[r.id] === 'review').length;
    }
  }

  function createFlashcardElement(r, displayNum) {
    const card = document.createElement('div');
    const isRevealed = state.reciteRevealedIds.has(r.id);
    const reciteStat = state.reciteStatus[r.id] || null;

    card.className = `flashcard ${isRevealed ? 'revealed' : ''}`;
    card.id = `flashcard-${r.id}`;

    // Header with badges
    const headerHtml = `
      <div class="flashcard-header">
        <div class="card-tags">
          <span class="type-tag short">${r.category}</span>
          ${r.sourceTag ? `<span class="exam-tag">${r.sourceTag}</span>` : ''}
          <span style="font-size: 0.72rem; color: var(--text-muted);">#${displayNum}</span>
        </div>
        <div>
          ${reciteStat === 'mastered' ? '<span style="font-size:0.75rem; color:var(--success-color); font-weight:700;">✓ 已熟练</span>' : ''}
          ${reciteStat === 'review' ? '<span style="font-size:0.75rem; color:var(--danger-color); font-weight:700;">✕ 待巩固</span>' : ''}
        </div>
      </div>
    `;

    // Front: Prompt / Concept
    const promptHtml = `<div class="flashcard-prompt">${r.title}</div>`;

    // Back: Answers & Points
    let answerHtml = '';
    if (!isRevealed) {
      answerHtml = `
        <div class="flashcard-reveal-hint">
          <span>🔍 点击卡片或此处，翻看标准答案与踩点清单</span>
        </div>
      `;
    } else {
      answerHtml = `
        <div class="flashcard-answer-box">
          <div class="explanation-title" style="color:var(--accent-color);">🎯 核心得分点/要点提纲（抽背踩点标准）:</div>
          <div class="points-list">
            ${(r.points || []).map((pt, i) => `
              <div class="point-item">
                <span style="font-weight:700; color:var(--accent-color);">${i + 1}.</span>
                <span>${pt}</span>
              </div>
            `).join('')}
          </div>

          <div style="margin-top: 12px; font-weight:700; color:var(--text-primary); font-size:0.85rem;">📝 原书/笔记标准答案:</div>
          <div class="flashcard-answer-text">${r.answer}</div>

          <div class="flashcard-status-row">
            <button class="recite-status-btn mastered ${reciteStat === 'mastered' ? 'active' : ''}" data-stat-rid="${r.id}" data-val="mastered">
              ✓ 抽背通过 (已背出)
            </button>
            <button class="recite-status-btn need-review ${reciteStat === 'review' ? 'active' : ''}" data-stat-rid="${r.id}" data-val="review">
              ✕ 遗忘/卡壳 (加入巩固)
            </button>
          </div>
          <button class="toggle-answer-btn" data-toggle-rid="${r.id}" style="margin-top:10px;">▲ 折叠隐藏答案</button>
        </div>
      `;
    }

    card.innerHTML = headerHtml + promptHtml + answerHtml;

    // Click card to toggle reveal if clicked outside buttons
    card.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      toggleFlashcardReveal(r.id);
    });

    const toggleBtn = card.querySelector('[data-toggle-rid]');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleFlashcardReveal(r.id);
      });
    }

    const statBtns = card.querySelectorAll('[data-stat-rid]');
    statBtns.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        handleReciteStatusChange(btn.dataset.statRid, btn.dataset.val);
      });
    });

    return card;
  }

  function toggleFlashcardReveal(rId) {
    if (state.reciteRevealedIds.has(rId)) {
      state.reciteRevealedIds.delete(rId);
    } else {
      state.reciteRevealedIds.add(rId);
    }
    refreshFlashcard(rId);
  }

  function refreshFlashcard(rId) {
    const r = state.recitations.find((item) => item.id === rId);
    if (!r) return;
    const cardEl = document.getElementById(`flashcard-${rId}`);
    if (cardEl) {
      const num = cardEl.querySelector('.card-tags span:last-child')?.textContent?.replace('#', '') || '1';
      const newCard = createFlashcardElement(r, num);
      cardEl.replaceWith(newCard);
    }
  }

  function handleReciteStatusChange(rId, statusVal) {
    if (state.reciteStatus[rId] === statusVal) {
      delete state.reciteStatus[rId];
    } else {
      state.reciteStatus[rId] = statusVal;
      if (statusVal === 'mastered') {
        if (navigator.vibrate) navigator.vibrate(25);
      } else {
        if (navigator.vibrate) navigator.vibrate([40, 40]);
      }
    }
    saveLocalData();
    updateRecitationCounts();
    refreshFlashcard(rId);
    triggerAutoSync();
  }

  function handleRandomReciteDraw() {
    const list = getFilteredRecitations();
    if (list.length === 0) {
      alert('当前筛选条件下暂无卡片');
      return;
    }

    const randIdx = Math.floor(Math.random() * list.length);
    const chosen = list[randIdx];

    // Collapse other cards and reveal only this chosen one
    state.reciteRevealedIds.add(chosen.id);
    renderQuestions();

    setTimeout(() => {
      const cardEl = document.getElementById(`flashcard-${chosen.id}`);
      if (cardEl) {
        cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        cardEl.classList.add('glow-highlight');
        setTimeout(() => {
          cardEl.classList.remove('glow-highlight');
        }, 3000);
      }
    }, 100);
  }

  // ================= 2. QUIZ QUESTIONS RENDERER =================
  function getFilteredQuestions() {
    const sourceList = state.currentMode === 'random' ? state.randomQuestions : state.questions;

    return sourceList.filter((q) => {
      if (state.currentMode !== 'random') {
        if (state.currentChapterId !== 'all' && q.chapterId !== state.currentChapterId) {
          return false;
        }
      }

      if (state.currentMode === 'wrong' && !state.wrongIds.has(q.id)) {
        return false;
      }
      if (state.currentMode === 'star' && !state.starredIds.has(q.id)) {
        return false;
      }

      if (state.currentFilterType !== 'all' && q.type !== state.currentFilterType) {
        return false;
      }

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

  function renderQuizCards() {
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

  function getEffectiveAnswer(qId) {
    if (state.currentMode === 'random') {
      return state.examSessionAnswers[qId] || null;
    }
    if (state.currentMode === 'wrong') {
      return state.wrongRetestAnswers[qId] || null;
    }
    if (state.currentMode === 'recite') {
      return null;
    }
    return state.userAnswers[qId] || null;
  }

  function createQuestionCard(q, displayNum) {
    const card = document.createElement('div');
    card.className = 'question-card';
    card.id = `card-${q.id}`;

    const isStarred = state.starredIds.has(q.id);
    const activeAnswer = getEffectiveAnswer(q.id);
    const isExamMode = state.currentMode === 'random';
    const isWrongMode = state.currentMode === 'wrong';

    const isRevealed = !isExamMode && state.revealedCardIds.has(q.id);
    const shouldShowExplanation = isExamMode ? state.examSubmitted : !!activeAnswer;

    const typeNames = { choice: '单选题', judge: '判断题', blank: '填空题', short: '简答题' };

    let actionButtonsHeader = '';
    if (activeAnswer && !isExamMode) {
      actionButtonsHeader = `<button class="re-test-btn" data-reset-qid="${q.id}">🔄 重做此题</button>`;
    }

    const headerHtml = `
      <div class="card-header">
        <div class="card-tags">
          <span class="type-tag ${q.type}">${typeNames[q.type] || '题目'}</span>
          ${q.examTag ? `<span class="exam-tag">${q.examTag}</span>` : ''}
          <span style="font-size: 0.72rem; color: var(--text-muted);">#${displayNum}</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          ${actionButtonsHeader}
          <button class="star-btn ${isStarred ? 'starred' : ''}" data-id="${q.id}" aria-label="收藏题目">
            ${isStarred ? '★' : '☆'}
          </button>
        </div>
      </div>
    `;

    let titleHtml = `<div class="question-title">${q.title}</div>`;
    if (q.type === 'blank') {
      if (shouldShowExplanation || isRevealed) {
        const highlightedTitle = q.title.replace(/【([^】]+)】/g, '<span style="color:var(--success-color); font-weight:700; text-decoration:underline;">$1</span>');
        titleHtml = `<div class="question-title">${highlightedTitle}</div>`;
      } else {
        const maskedTitle = q.title.replace(/【([^】]+)】/g, '<span style="border-bottom:2px dashed var(--accent-color); padding: 0 10px; color:transparent; background:var(--accent-light); border-radius:3px;">____</span>');
        titleHtml = `<div class="question-title">${maskedTitle}</div>`;
      }
    }

    let bodyHtml = '';

    // 1. Choice
    if (q.type === 'choice') {
      bodyHtml = `
        <div class="options-list">
          ${q.options.map((opt) => {
            const optKey = opt.trim().charAt(0).toUpperCase();
            let optClass = 'option-btn';

            if (isExamMode && !state.examSubmitted) {
              if (activeAnswer && activeAnswer.selectedOption === optKey) {
                optClass += ' selected-exam';
              }
            } else if (activeAnswer) {
              if (optKey === q.answer) {
                optClass += ' show-correct';
              }
              if (activeAnswer.selectedOption === optKey) {
                optClass += activeAnswer.isCorrect ? ' selected-correct' : ' selected-wrong';
              }
            }

            const isDisabled = isExamMode && state.examSubmitted;

            return `
              <button class="${optClass}" data-qid="${q.id}" data-opt="${optKey}" ${isDisabled ? 'disabled' : ''}>
                ${opt}
              </button>
            `;
          }).join('')}
        </div>
      `;

      if (isWrongMode && activeAnswer && activeAnswer.isCorrect) {
        bodyHtml += `
          <div class="conquer-banner">
            <span>🎉 恭喜！本题已重新攻克！</span>
            <button class="action-btn primary mini remove-wrong-action-btn" data-remove-wrong-qid="${q.id}">✓ 移出错题本</button>
          </div>
        `;
      }

      if (shouldShowExplanation) {
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
    // 2. Judge
    else if (q.type === 'judge') {
      let trueClass = 'judge-btn';
      let falseClass = 'judge-btn';

      if (isExamMode && !state.examSubmitted) {
        if (activeAnswer && activeAnswer.selectedOption === '正确') trueClass += ' selected-exam';
        if (activeAnswer && activeAnswer.selectedOption === '错误') falseClass += ' selected-exam';
      } else if (activeAnswer) {
        if (q.answer === '正确') trueClass += ' show-correct';
        if (q.answer === '错误') falseClass += ' show-correct';

        if (activeAnswer.selectedOption === '正确') {
          trueClass += activeAnswer.isCorrect ? ' selected-correct' : ' selected-wrong';
        } else if (activeAnswer.selectedOption === '错误') {
          falseClass += activeAnswer.isCorrect ? ' selected-correct' : ' selected-wrong';
        }
      }

      const isDisabled = isExamMode && state.examSubmitted;

      bodyHtml = `
        <div class="judge-options-row">
          <button class="${trueClass}" data-qid="${q.id}" data-judge="正确" ${isDisabled ? 'disabled' : ''}>
            ✓ 正确
          </button>
          <button class="${falseClass}" data-qid="${q.id}" data-judge="错误" ${isDisabled ? 'disabled' : ''}>
            ✕ 错误
          </button>
        </div>
      `;

      if (isWrongMode && activeAnswer && activeAnswer.isCorrect) {
        bodyHtml += `
          <div class="conquer-banner">
            <span>🎉 恭喜！本题已重新攻克！</span>
            <button class="action-btn primary mini remove-wrong-action-btn" data-remove-wrong-qid="${q.id}">✓ 移出错题本</button>
          </div>
        `;
      }

      if (shouldShowExplanation) {
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
    // 3. Blank
    else if (q.type === 'blank') {
      const userText = activeAnswer ? (activeAnswer.userText || '') : '';

      bodyHtml = `
        <div class="blank-interactive-box">
          <input type="text"
            class="blank-text-input"
            id="blank-input-${q.id}"
            placeholder="输入你的填空词（多个关键词可用逗号或空格隔开）..."
            value="${escapeHtml(userText)}"
            ${isExamMode && state.examSubmitted ? 'disabled' : ''}
          />
          <div class="blank-actions-row">
            <button class="action-btn primary check-blank-btn" data-qid="${q.id}" style="flex:1;">
              ${activeAnswer ? '重新核对答案' : '🔍 提交核对填空'}
            </button>
            ${activeAnswer && !isExamMode ? `
              <button class="mini-score-btn correct ${activeAnswer.isCorrect ? 'active' : ''}" data-override-qid="${q.id}" data-val="true">
                ✓ 判定答对
              </button>
              <button class="mini-score-btn wrong ${!activeAnswer.isCorrect ? 'active' : ''}" data-override-qid="${q.id}" data-val="false">
                ✕ 判定答错
              </button>
            ` : ''}
          </div>
        </div>
      `;

      if (isWrongMode && activeAnswer && activeAnswer.isCorrect) {
        bodyHtml += `
          <div class="conquer-banner">
            <span>🎉 恭喜！本填空题已重新攻克！</span>
            <button class="action-btn primary mini remove-wrong-action-btn" data-remove-wrong-qid="${q.id}">✓ 移出错题本</button>
          </div>
        `;
      }

      if (shouldShowExplanation) {
        const isCorrect = activeAnswer && activeAnswer.isCorrect;
        bodyHtml += `
          <div class="blank-card-answer" style="border-color:${isCorrect ? 'var(--success-color)' : 'var(--danger-color)'}; background:${isCorrect ? 'var(--success-light)' : 'var(--danger-light)'}; color:${isCorrect ? 'var(--success-color)' : 'var(--danger-color)'};">
            <div>${isCorrect ? '🎉 填空回答正确！' : '❌ 存在偏差或未答完整'}</div>
            <div style="margin-top:4px;">✨ 标准填空参考: <b>${q.answer}</b></div>
          </div>
          ${q.explanation ? `<div class="explanation-box"><div class="explanation-text">${q.explanation}</div></div>` : ''}
        `;
      }
    }
    // 4. Short Answer
    else if (q.type === 'short') {
      const userText = activeAnswer ? (activeAnswer.userText || '') : '';
      const checkedPoints = (activeAnswer && activeAnswer.checkedPoints) || [];
      const selfScore = activeAnswer ? (activeAnswer.score || 0) : null;

      bodyHtml = `
        <div class="short-input-box">
          <textarea
            class="short-textarea"
            id="short-input-${q.id}"
            placeholder="写下你的核心答题要点、逻辑思路或关键词回忆..."
            rows="3"
          >${escapeHtml(userText)}</textarea>
          <button class="toggle-answer-btn" data-toggle="${q.id}">
            ${isRevealed ? '▲ 收起评分标准与参考答案' : '📖 展开得分点核对与参考答案'}
          </button>
        </div>
      `;

      if (isWrongMode && activeAnswer && activeAnswer.isCorrect) {
        bodyHtml += `
          <div class="conquer-banner">
            <span>🎉 恭喜！本大题已达标攻克！</span>
            <button class="action-btn primary mini remove-wrong-action-btn" data-remove-wrong-qid="${q.id}">✓ 移出错题本</button>
          </div>
        `;
      }

      if (isRevealed || (isExamMode && state.examSubmitted)) {
        bodyHtml += `
          <div class="explanation-box" style="margin-top: 6px;">
            <div class="explanation-title">🎯 核心得分点核对清单（勾选你已答出的要点）</div>
            <div class="points-checklist">
              ${(q.points || []).map((pt, i) => `
                <label class="point-check-item">
                  <input type="checkbox"
                    class="point-cb"
                    data-qid="${q.id}"
                    data-idx="${i}"
                    ${checkedPoints.includes(i) ? 'checked' : ''}
                  />
                  <span><b>点 ${i + 1}:</b> ${pt}</span>
                </label>
              `).join('')}
            </div>

            <div class="quick-score-row">
              <span class="quick-score-label">本题自评:</span>
              <button class="score-pill-btn ${selfScore === 5 ? 'active-full' : ''}" data-score-qid="${q.id}" data-val="5">满分 (5分)</button>
              <button class="score-pill-btn ${selfScore === 3 ? 'active-pass' : ''}" data-score-qid="${q.id}" data-val="3">及格 (3分)</button>
              <button class="score-pill-btn ${selfScore === 0 ? 'active-zero' : ''}" data-score-qid="${q.id}" data-val="0">未掌握 (0分)</button>
            </div>

            <div style="margin-top: 12px; font-weight:700; color:var(--text-primary); font-size:0.85rem;">📝 完整标准答案:</div>
            <div class="explanation-text" style="margin-top: 4px;">${q.answer}</div>
          </div>
        `;
      }
    }

    card.innerHTML = headerHtml + titleHtml + bodyHtml;

    // Attach card event listeners
    const starBtn = card.querySelector('.star-btn');
    if (starBtn) {
      starBtn.addEventListener('click', () => toggleStar(q.id));
    }

    const resetBtn = card.querySelector('[data-reset-qid]');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => resetQuestionAnswer(q.id));
    }

    const removeWrongBtn = card.querySelector('[data-remove-wrong-qid]');
    if (removeWrongBtn) {
      removeWrongBtn.addEventListener('click', () => removeFromWrongNotebook(q.id));
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

    const checkBlankBtn = card.querySelector('.check-blank-btn');
    if (checkBlankBtn) {
      checkBlankBtn.addEventListener('click', () => {
        const inputEl = document.getElementById(`blank-input-${q.id}`);
        evaluateBlankAnswer(q.id, inputEl ? inputEl.value : '');
      });
    }

    const overrideBtns = card.querySelectorAll('[data-override-qid]');
    overrideBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        overrideBlankEvaluation(btn.dataset.overrideQid, btn.dataset.val === 'true');
      });
    });

    const shortTextarea = card.querySelector(`#short-input-${q.id}`);
    if (shortTextarea) {
      shortTextarea.addEventListener('input', (e) => {
        saveShortDraft(q.id, e.target.value);
      });
    }

    const pointCbs = card.querySelectorAll('.point-cb');
    pointCbs.forEach((cb) => {
      cb.addEventListener('change', () => {
        handlePointCheckChange(cb.dataset.qid);
      });
    });

    const scorePillBtns = card.querySelectorAll('[data-score-qid]');
    scorePillBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        handleShortQuickScore(btn.dataset.scoreQid, parseInt(btn.dataset.val, 10));
      });
    });

    const toggleBtn = card.querySelector('[data-toggle]');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => toggleCardReveal(q.id));
    }

    return card;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // ================= ACTION HANDLERS =================
  function handleChoiceClick(qId, selectedOption) {
    const q = state.questions.find((item) => item.id === qId);
    if (!q) return;

    const isCorrect = selectedOption === q.answer;

    if (state.currentMode === 'random') {
      if (state.examSubmitted) return;
      state.examSessionAnswers[qId] = { selectedOption, isCorrect, timestamp: Date.now() };
    } else if (state.currentMode === 'wrong') {
      state.wrongRetestAnswers[qId] = { selectedOption, isCorrect, timestamp: Date.now() };
      state.userAnswers[qId] = { selectedOption, isCorrect, timestamp: Date.now() };
      if (!isCorrect) {
        state.wrongIds.add(qId);
        if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
      } else {
        if (navigator.vibrate) navigator.vibrate(25);
      }
      saveLocalData();
      triggerAutoSync();
    } else {
      state.userAnswers[qId] = { selectedOption, isCorrect, timestamp: Date.now() };
      if (!isCorrect) {
        state.wrongIds.add(qId);
        if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
      } else {
        if (state.wrongIds.has(qId)) state.wrongIds.delete(qId);
        if (navigator.vibrate) navigator.vibrate(25);
      }
      saveLocalData();
      triggerAutoSync();
    }

    updateStats();
    refreshCard(qId);
  }

  function handleJudgeClick(qId, selectedVal) {
    const q = state.questions.find((item) => item.id === qId);
    if (!q) return;

    const isCorrect = selectedVal === q.answer;

    if (state.currentMode === 'random') {
      if (state.examSubmitted) return;
      state.examSessionAnswers[qId] = { selectedOption: selectedVal, isCorrect, timestamp: Date.now() };
    } else if (state.currentMode === 'wrong') {
      state.wrongRetestAnswers[qId] = { selectedOption: selectedVal, isCorrect, timestamp: Date.now() };
      state.userAnswers[qId] = { selectedOption: selectedVal, isCorrect, timestamp: Date.now() };
      if (!isCorrect) {
        state.wrongIds.add(qId);
        if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
      } else {
        if (navigator.vibrate) navigator.vibrate(25);
      }
      saveLocalData();
      triggerAutoSync();
    } else {
      state.userAnswers[qId] = { selectedOption: selectedVal, isCorrect, timestamp: Date.now() };
      if (!isCorrect) {
        state.wrongIds.add(qId);
        if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
      } else {
        if (state.wrongIds.has(qId)) state.wrongIds.delete(qId);
        if (navigator.vibrate) navigator.vibrate(25);
      }
      saveLocalData();
      triggerAutoSync();
    }

    updateStats();
    refreshCard(qId);
  }

  function evaluateBlankAnswer(qId, rawInput) {
    const q = state.questions.find((item) => item.id === qId);
    if (!q) return;

    const input = (rawInput || '').trim().toLowerCase();
    const standard = (q.answer || '').toLowerCase();

    const keywords = standard.split(/[、,，\s/]+/).map((s) => s.trim()).filter((s) => s.length > 0);

    let matchCount = 0;
    keywords.forEach((kw) => {
      if (input.includes(kw)) matchCount++;
    });

    const isCorrect = keywords.length > 0 && (matchCount === keywords.length || (keywords.length >= 2 && matchCount >= keywords.length * 0.6));

    const answerObj = {
      userText: rawInput,
      isCorrect: isCorrect,
      timestamp: Date.now(),
    };

    if (state.currentMode === 'random') {
      state.examSessionAnswers[qId] = answerObj;
    } else if (state.currentMode === 'wrong') {
      state.wrongRetestAnswers[qId] = answerObj;
      state.userAnswers[qId] = answerObj;
      if (!isCorrect) {
        state.wrongIds.add(qId);
      }
      saveLocalData();
      triggerAutoSync();
    } else {
      state.userAnswers[qId] = answerObj;
      if (!isCorrect) {
        state.wrongIds.add(qId);
        if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
      } else {
        if (state.wrongIds.has(qId)) state.wrongIds.delete(qId);
        if (navigator.vibrate) navigator.vibrate(25);
      }
      saveLocalData();
      triggerAutoSync();
    }

    updateStats();
    refreshCard(qId);
  }

  function overrideBlankEvaluation(qId, forceCorrect) {
    const targetMap = state.currentMode === 'wrong' ? state.wrongRetestAnswers : state.userAnswers;
    const existing = targetMap[qId] || { userText: '', timestamp: Date.now() };
    existing.isCorrect = forceCorrect;
    existing.timestamp = Date.now();
    targetMap[qId] = existing;

    if (state.currentMode === 'wrong') {
      state.userAnswers[qId] = existing;
      if (!forceCorrect) {
        state.wrongIds.add(qId);
      }
    } else {
      if (!forceCorrect) {
        state.wrongIds.add(qId);
      } else {
        state.wrongIds.delete(qId);
      }
    }

    saveLocalData();
    updateStats();
    refreshCard(qId);
    triggerAutoSync();
  }

  function saveShortDraft(qId, text) {
    const targetMap = state.currentMode === 'wrong' ? state.wrongRetestAnswers : (state.currentMode === 'random' ? state.examSessionAnswers : state.userAnswers);
    const existing = targetMap[qId] || { timestamp: Date.now() };
    existing.userText = text;
    targetMap[qId] = existing;
    if (state.currentMode !== 'random') {
      saveLocalData();
    }
  }

  function handlePointCheckChange(qId) {
    const cardEl = document.getElementById(`card-${qId}`);
    if (!cardEl) return;

    const checkedBoxes = cardEl.querySelectorAll('.point-cb:checked');
    const checkedIdxs = Array.from(checkedBoxes).map((cb) => parseInt(cb.dataset.idx, 10));

    const q = state.questions.find((item) => item.id === qId);
    const totalPoints = (q && q.points && q.points.length) || 1;

    const targetMap = state.currentMode === 'wrong' ? state.wrongRetestAnswers : (state.currentMode === 'random' ? state.examSessionAnswers : state.userAnswers);
    const existing = targetMap[qId] || { userText: '', timestamp: Date.now() };
    existing.checkedPoints = checkedIdxs;

    const ratio = checkedIdxs.length / totalPoints;
    let score = 0;
    if (ratio >= 0.75) score = 5;
    else if (ratio >= 0.4) score = 3;
    existing.score = score;
    existing.isCorrect = score >= 3;
    existing.timestamp = Date.now();
    targetMap[qId] = existing;

    if (state.currentMode === 'wrong') {
      state.userAnswers[qId] = existing;
      if (!existing.isCorrect) state.wrongIds.add(qId);
    } else if (state.currentMode !== 'random') {
      if (!existing.isCorrect) state.wrongIds.add(qId);
      else state.wrongIds.delete(qId);
    }

    saveLocalData();
    updateStats();
    refreshCard(qId);
    triggerAutoSync();
  }

  function handleShortQuickScore(qId, scoreVal) {
    const targetMap = state.currentMode === 'wrong' ? state.wrongRetestAnswers : (state.currentMode === 'random' ? state.examSessionAnswers : state.userAnswers);
    const existing = targetMap[qId] || { userText: '', timestamp: Date.now() };
    existing.score = scoreVal;
    existing.isCorrect = scoreVal >= 3;
    existing.timestamp = Date.now();
    targetMap[qId] = existing;

    if (state.currentMode === 'wrong') {
      state.userAnswers[qId] = existing;
      if (!existing.isCorrect) state.wrongIds.add(qId);
    } else if (state.currentMode !== 'random') {
      if (!existing.isCorrect) state.wrongIds.add(qId);
      else state.wrongIds.delete(qId);
    }

    saveLocalData();
    updateStats();
    refreshCard(qId);
    triggerAutoSync();
  }

  function removeFromWrongNotebook(qId) {
    state.wrongIds.delete(qId);
    delete state.wrongRetestAnswers[qId];
    saveLocalData();
    updateCounts();
    updateStats();
    triggerAutoSync();
    renderQuestions();
  }

  function resetQuestionAnswer(qId) {
    if (state.currentMode === 'wrong') {
      delete state.wrongRetestAnswers[qId];
    } else if (state.currentMode === 'random') {
      delete state.examSessionAnswers[qId];
    } else {
      delete state.userAnswers[qId];
    }
    saveLocalData();
    updateStats();
    refreshCard(qId);
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
    triggerAutoSync();
  }

  function toggleCardReveal(qId) {
    if (state.revealedCardIds.has(qId)) {
      state.revealedCardIds.delete(qId);
    } else {
      state.revealedCardIds.add(qId);
    }
    refreshCard(qId);
  }

  function refreshCard(qId) {
    const q = state.questions.find((item) => item.id === qId);
    if (!q) return;
    const cardEl = document.getElementById(`card-${qId}`);
    if (cardEl) {
      const num = cardEl.querySelector('.card-tags span:last-child')?.textContent?.replace('#', '') || '1';
      const newCard = createQuestionCard(q, num);
      cardEl.replaceWith(newCard);
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
