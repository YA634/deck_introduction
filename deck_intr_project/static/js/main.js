// メニュー制御（バージョン2025-1）
$(() => {
  const $menubar = $('#menubar');
  const $menubarHdr = $('#menubar_hdr');
  const breakPoint = 900; // ブレイクポイント
  const HIDE_MENUBAR_IF_HDR_HIDDEN = false;

  const isTouchDevice =
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0;

  // 処理の呼び出し頻度を抑制する
  const debounce = (fn, wait) => {
    let timerId;
    return (...args) => {
      clearTimeout(timerId);
      timerId = setTimeout(() => fn(...args), wait);
    };
  };

  // ドロップダウンメニューの初期化
  const initDropdown = ($menu, isTouch) => {
    $menu.find('ul li').each((_, el) => {
      const $li = $(el);
      if ($li.find('ul').length) {
        $li.addClass('ddmenu_parent');
        $li.children('a').addClass('ddmenu');
      }
    });

    if (isTouch) {
      // タッチデバイス：タップで開閉
      $menu.find('.ddmenu').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const $dropdownMenu = $(this).siblings('ul');
        if ($dropdownMenu.is(':visible')) {
          $dropdownMenu.hide();
        } else {
          $menu.find('.ddmenu_parent ul').hide();
          $dropdownMenu.show();
        }
      });
    } else {
      // PC：ホバーで開閉
      $menu.find('.ddmenu_parent').hover(
        function () { $(this).children('ul').show(); },
        function () { $(this).children('ul').hide(); }
      );
    }
  };

  // ハンバーガーメニューの開閉制御
  const initHamburger = ($hamburger, $menu) => {
    $hamburger.on('click', function () {
      $(this).toggleClass('ham');
      const isOpen = $(this).hasClass('ham');
      const isNarrow = $(window).width() < breakPoint;

      $menu.toggle(isOpen);
      if (isNarrow) {
        $('body').toggleClass('noscroll', isOpen);
      }
      $menu.find('.ddmenu_parent ul').hide();
    });
  };

  // リサイズ時のレスポンシブ表示制御
  const handleResize = debounce(() => {
    const windowWidth = $(window).width();
    const isNarrow = windowWidth < breakPoint;

    $('body').toggleClass('small-screen', isNarrow);
    $('body').toggleClass('large-screen', !isNarrow);

    if (!isNarrow) {
      $menubarHdr.removeClass('ham');
      $menubar.find('.ddmenu_parent ul').hide();
      $('body').removeClass('noscroll');

      if (HIDE_MENUBAR_IF_HDR_HIDDEN) {
        $menubarHdr.hide();
        $menubar.hide();
      } else {
        $menubarHdr.hide();
        $menubar.show();
      }
    } else {
      $menubarHdr.show();
      if (!$menubarHdr.hasClass('ham')) {
        $menubar.hide();
        $('body').removeClass('noscroll');
      }
    }
  }, 200);

  initDropdown($menubar, isTouchDevice);
  initHamburger($menubarHdr, $menubar);
  handleResize();
  $(window).on('resize', handleResize);

  // アンカーリンククリック時にハンバーガーメニューを閉じる
  $menubar.find('a[href^="#"]').on('click', function () {
    if ($(this).hasClass('ddmenu')) return;

    if ($menubarHdr.is(':visible') && $menubarHdr.hasClass('ham')) {
      $menubarHdr.removeClass('ham');
      $menubar.hide();
      $menubar.find('.ddmenu_parent ul').hide();
      $('body').removeClass('noscroll');
    }
  });

  // 他のメニューにドロップダウンだけ適用したい場合の例：
  // initDropdown($('header nav'), isTouchDevice);
});


// スムーススクロール（バージョン2024-1）
$(() => {
  const $topButton = $('.pagetop');
  const scrollShowClass = 'pagetop-show';

  const smoothScroll = (target) => {
    const scrollTo = target === '#' ? 0 : $(target).offset().top;
    $('html, body').animate({ scrollTop: scrollTo }, 500);
  };

  $('a[href^="#"], .pagetop').on('click', function (e) {
    e.preventDefault();
    const id = $(this).attr('href') || '#';
    smoothScroll(id);
  });

  $topButton.hide();
  $(window).on('scroll', function () {
    const isPastThreshold = $(this).scrollTop() >= 300;
    $topButton
      .toggleClass(scrollShowClass, isPastThreshold)
      [isPastThreshold ? 'fadeIn' : 'fadeOut']();
  });

  // URLにハッシュがある場合、一度トップで待機してからスムーススクロール
  if (window.location.hash) {
    $('html, body').scrollTop(0);
    setTimeout(() => smoothScroll(window.location.hash), 700);
  }
});


// スライドショー
$(() => {
  $('#mainimg').each(function () {
    const $root = $(this);
    const slides = $root.find('.slide');
    const slideCount = slides.length;
    const INTERVAL = 5000;
    const FADE_MS = 1000;

    let currentIndex = 0;
    let autoTimer = null;
    let isAnimating = false;

    const $indicators = $root.find('.slide-indicators').empty();
    for (let i = 0; i < slideCount; i++) {
      $indicators.append(`<span class="indicator" data-index="${i}"></span>`);
    }
    const $dots = $indicators.find('.indicator');

    slides.css('opacity', 0).removeClass('active');
    slides.eq(0).css('opacity', 1).addClass('active');
    $dots.removeClass('active').eq(0).addClass('active');

    const setActive = (nextIndex) => {
      if (nextIndex === currentIndex) return;
      isAnimating = true;

      slides.eq(currentIndex).css('opacity', 0).removeClass('active');
      slides.eq(nextIndex).css('opacity', 1).addClass('active');
      $dots.eq(currentIndex).removeClass('active');
      $dots.eq(nextIndex).addClass('active');

      currentIndex = nextIndex;
      setTimeout(() => { isAnimating = false; }, FADE_MS);
    };

    const restartTimer = () => {
      clearTimeout(autoTimer);
      autoTimer = setTimeout(next, INTERVAL);
    };

    function next() {
      setActive((currentIndex + 1) % slideCount);
      restartTimer();
    }

    $dots.on('click', function () {
      const to = $(this).data('index');
      if (isAnimating) return;
      if (to === currentIndex) return restartTimer();
      setActive(to);
      restartTimer();
    });

    restartTimer();
  });
});


// 詳細ページのサムネイル切り替え（画像/動画 両対応）
$(() => {
  // サムネvideoの初期設定（コントロール無効化、iOS対策、再生アイコン追加）
  $('.thumbnail video').each(function () {
    const $v = $(this);
    const videoEl = this;

    $v.attr({
      preload: 'metadata',
      muted: true,
      playsinline: true
    });
    videoEl.removeAttribute('controls');

    try {
      videoEl.pause();
      videoEl.currentTime = 0.1; // iOSは0秒だと描画されないことがあるため
    } catch (e) {}

    if (!$v.parent().hasClass('thumb-wrap')) {
      $v.wrap('<span class="thumb-wrap is-video"></span>');
      $v.after('<span class="thumb-play" aria-hidden="true"><i class="fa-solid fa-play fas fa-play"></i></span>');
    }
  });

  // サムネ要素（img, video）から表示用の要素を生成
  const createViewerEl = ($media) => {
    if ($media.is('img')) {
      return $('<img>').attr('src', $media.attr('src'));
    }
    if ($media.is('video')) {
      const src = $media.attr('src') || $media.find('source:first').attr('src');
      if (!src) return null;
      return $('<video>').attr({
        src,
        controls: true,
        playsinline: true,
        preload: 'metadata',
        loop: true
      });
    }
    return null;
  };

  // 初期表示：直後の.thumbnailの最初のimgかvideoを表示
  $('.thumbnail-view').each(function () {
    const $view = $(this);
    const $first = $view.next('.thumbnail').find('img,video').first();
    const $el = createViewerEl($first);
    if (!$el) return;

    $view.empty().append($el);

    // 動画の場合、iOSで真っ白にならないよう0.1秒目を表示させる
    if ($el.is('video')) {
      try {
        $el[0].load();
        $el[0].currentTime = 0.1;
      } catch (e) {}
    }
  });

  // サムネイルクリック（イベント委譲）
  $('.thumbnail').on('pointerdown', function (e) {
    const $media = $(e.target).closest('img,video', this);
    if (!$media.length) return;
    e.preventDefault();

    if ($media.is('video') && $media[0].pause) $media[0].pause();

    const $targetView = $(this).prev('.thumbnail-view');
    const $nextEl = createViewerEl($media);
    if (!$nextEl) return;

    // hide()だとiOSで描画されないため、透明度を操作してフェードさせる
    $nextEl.css('opacity', 0);

    $targetView.find('img,video').fadeOut(400, () => {
      $targetView.empty().append($nextEl);

      if ($nextEl.is('video')) {
        try {
          $nextEl[0].load();
          $nextEl[0].currentTime = 0.1;
        } catch (e) {}
      }

      $nextEl.animate({ opacity: 1 }, 400);
    });
  });
});


// 画面幅1000px未満でclassの付け外し
$(() => {
  const mq = window.matchMedia('(max-width: 1000px)');
  const apply = () => $('.fix-col').toggleClass('window-s', mq.matches);

  apply();
  if (mq.addEventListener) {
    mq.addEventListener('change', apply);
  } else {
    mq.addListener(apply); // 古いブラウザ向け
  }
});


// 文字サイズ変更ボタン
$(() => {
  const changeFontSize = (buttonID, className) => {
    $('html').removeClass('f-small f-large').addClass(className);
    $('#f-size .current').removeClass('current');
    $(buttonID).addClass('current');
    window.sessionStorage.setItem('CHSIZE', className);
  };

  const storedSize = window.sessionStorage.getItem('CHSIZE');
  if (storedSize) {
    changeFontSize(`#f-size #${storedSize}`, storedSize);
  } else {
    changeFontSize('#f-small', 'f-small'); // デフォルトは「小」
  }

  $('#f-size #f-small').on('click', () => changeFontSize('#f-small', 'f-small'));
  $('#f-size #f-large').on('click', () => changeFontSize('#f-large', 'f-large'));
});


// 汎用開閉処理
$(() => {
  $('.openclose1').next().hide();
  $('.openclose1').on('click', function () {
    $(this).next().slideToggle();
    $('.openclose1').not(this).next().slideUp();
  });
});