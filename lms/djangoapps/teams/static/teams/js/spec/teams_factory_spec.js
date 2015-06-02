define(["jquery", "teams/js/teams_tab_factory"],
    function($, TeamsTabFactory) {
        'use strict';
       
        describe("teams django app", function() {
            var teamsTab;

            beforeEach(function() {
                setFixtures("<div class='team-tab-content'></div>" +
                            "<div class='team-tab-header'></div>");
                teamsTab = new TeamsTabFactory({
                    title: 'Test title',
                    description: 'Test description'
                });
            });

            it("can load templates", function() {
                expect($("body").text()).toContain("This is the new Teams tab");
            });

            it("displays a header", function() {
                expect($("body").text()).toContain("Test title");
                expect($("body").text()).toContain("Test description");
            });
        });
    }
);
