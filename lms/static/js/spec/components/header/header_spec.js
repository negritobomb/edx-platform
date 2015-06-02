(function (define) {
    'use strict';

    define(['jquery',
            'underscore',
            'js/components/header/views/header',
            'js/components/header/models/header'
           ],
           function($, _, HeaderView, HeaderModel) {

               describe('header component view', function () {
                   var model, view;

                   beforeEach(function () {
                       setFixtures('<div class="test-header"></div>');
                       model = new HeaderModel({
                           title: 'Test title',
                           description: 'Test description'
                       });
                       view = new HeaderView({
                           model: model,
                           el: $('.test-header')
                       });
                       view.render();
                   });

                   it('can render itself', function () {
                       expect($('.test-header').text()).toContain('Test title');
                       expect($('.test-header').text()).toContain('Test description');
                   });

                   it('does not show breadcrumbs by default', function () {
                       expect($('.test-header').html()).not.toContain('<nav class="breadcrumbs">');
                   });

                   it('shows breadcrumbs if they are supplied', function () {
                       model.set('breadcrumbs', [
                           {url: 'url1', title: 'Crumb 1'},
                           {url: 'url2', title: 'Crumb 2'}
                       ]);
                       view.render();
                       expect($('.test-header').html()).toContain('<nav class="breadcrumbs">');
                       var urls = _.map($('.nav-item'), function (el) {
                           return $(el).attr('href');
                       });
                       expect(urls).toEqual(['url1', 'url2']);
                       var titles = _.map($('.nav-item'), function (el) {
                           return $(el).text();
                       });
                       expect(titles).toEqual(['Crumb 1', 'Crumb 2']);
                   });
               });
           }
          );
}).call(this, define || RequireJS.define);
