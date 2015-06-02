;(function (define) {
    'use strict';

    define(['jquery',
            'teams/js/views/teams_tab',
            'js/components/header/views/header',
            'js/components/header/models/header'],
           function ($, TeamsTabView, HeaderView, HeaderModel) {
               return function (headerInfo) {
                   var headerModel = new HeaderModel(headerInfo),
                       headerView = new HeaderView({
                           model: headerModel,
                           el: $('.team-tab-header')
                       }),
                       view = new TeamsTabView({
                           el: $('.team-tab-content')
                       });
                   view.render();
                   headerView.render();
               };
           });
}).call(this, define || RequireJS.define);
