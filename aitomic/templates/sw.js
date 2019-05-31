var filesToCache = [
    '/',
    '/signup/',
    '/accounts/login/',
    '/about/',
    '/userGuide/',
    '/faq/',
    '/changeLog/',
    '/static/js/background.js',
    '/static/js/noise.js',
    '/static/js/translate.js',
    '/static/js/comments.js',
    '/static/js/error.js',
    '/static/js/manifest.json',
    '/static/js/particles.json',
    '/static/img/logo.png',
    '/static/img/main-bg.jpg',
    '/static/img/main-profit.jpg',
    '/static/img/main-search.jpg',
    '/static/img/main-searchy.jpg',
    '/static/js/bulma-steps.min.js',
    'https://use.fontawesome.com/releases/v5.3.1/js/all.js',
    'https://code.jquery.com/jquery-3.3.1.js',
    'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.44.0/codemirror.js',
    'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.44.0/mode/python/python.js',
    'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.45.0/addon/display/placeholder.js',
    'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.min.css',
    'https://cdn.jsdelivr.net/npm/bulma-pageloader@2.1.0/dist/css/bulma-pageloader.min.css',
    'https://unpkg.com/aos@2.3.1/dist/aos.js',
    'https://unpkg.com/bulma-modal-fx@1.1.1/dist/js/modal-fx.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.44.0/codemirror.min.css',
    '/static/bulma/css/style.css',
    'https://unpkg.com/bulma-modal-fx/dist/css/modal-fx.min.css',
    'https://unpkg.com/aos@2.3.1/dist/aos.css',
    'https://cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.js',
    'https://unpkg.com/bulma-modal-fx@1.1.1/dist/css/modal-fx.min.css',
    'https://fonts.googleapis.com/css?family=Raleway',
    'https://fonts.gstatic.com/s/raleway/v13/1Ptug8zYS_SKggPNyC0ITw.woff2',
    '/static/img/icon.png',
    '/static/img/icons/144.png',
    '/static/js/AOSinit.js',
    '/static/js/navInit.js'
];
importScripts('https://storage.googleapis.com/workbox-cdn/releases/4.3.1/workbox-sw.js');

for (let i = 0; i < filesToCache.length; i++) {
    workbox.routing.registerRoute(filesToCache[i],
      new workbox.strategies.NetworkFirst()
    );
}

