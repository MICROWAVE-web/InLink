$(window).load(function () {
    $('#check_links').on('click', function () {
        $("#check_links").toggleClass('banner-btn-3 banner-btn-3-active');
        $("#list-of-links").toggleClass('showed hidden');
    });
    $('#check_photos').on('click', function () {
        $("#check_photos").toggleClass('banner-btn-3 banner-btn-3-active');
        $("#list-of-images").toggleClass('showed hidden');
    });
    $('#check_videos').on('click', function () {
        $("#check_videos").toggleClass('banner-btn-3 banner-btn-3-active');
        $("#list-of-videos").toggleClass('showed hidden');
    });
    $('#scroll_top').on('click', function () {
        $('html, body').animate({scrollTop: 0}, 600);
    });
    $('#go_service').on('click', function () {
        $('html, body').animate({scrollTop: 500}, 600);
    });
    checkCookies();
});

function checkCookies() {
    let cookieDate = localStorage.getItem('cookieDate');
    let cookieNotification = document.getElementById('cookie_notification');
    let cookieBtn = cookieNotification.querySelector('.cookie_accept');

    // Если записи про кукисы нет или она просрочена на 1 год, то показываем информацию про кукисы
    if (!cookieDate || (+cookieDate + 31536000000) < Date.now()) {
        cookieNotification.classList.add('show');
    }

    // При клике на кнопку, в локальное хранилище записывается текущая дата в системе UNIX
    cookieBtn.addEventListener('click', function () {
        localStorage.setItem('cookieDate', Date.now());
        cookieNotification.classList.remove('show');
    })
}

