/* GẠC MĂNG RÊ — cấu hình liên hệ đặt phần, nền thanh điều hướng khi cuộn, hiệu ứng hiện dần.
   Chỉ cần sửa 2 dòng dưới đây. Mọi nút Zalo/Messenger trên site sẽ tự cập nhật. */
(function () {
  var CONTACT = {
    zalo: 'https://zalo.me/0936752494',
    messenger: 'https://m.me/phannhuquynh1314'
  };

  document.querySelectorAll('[data-contact="zalo"]').forEach(function (a) { a.href = CONTACT.zalo; });
  document.querySelectorAll('[data-contact="messenger"]').forEach(function (a) { a.href = CONTACT.messenger; });

  var nav = document.querySelector('.nav.nav--fixed');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('is-solid', window.scrollY > 60); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  var items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  items.forEach(function (el) { io.observe(el); });
})();
