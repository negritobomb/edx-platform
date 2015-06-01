;(function (define) {
    'use strict';

    define(['jquery',
            'teams/js/views/teams_tab',
            'js/components/header/views/header',
            'js/components/header/models/header'],
           function ($, TeamsTabView, HeaderView, HeaderModel) {
             return function (headerInfo) {
               var view = new TeamsTabView({
                 el: $('.team-tab-content')
               });
               view.render();
               var headerModel = new HeaderModel(headerInfo);
               var headerView = new HeaderView({
                 model: headerModel,
                 el: $('.team-tab-header')
               });
               headerView.render();
             };
           });
}).call(this, define || RequireJS.define);
