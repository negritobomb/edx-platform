var edx = edx || {};

(function(Backbone, $, _, gettext) {
    'use strict';

    edx.instructor_dashboard = edx.instructor_dashboard || {};
    edx.instructor_dashboard.ecommerce = {};

    edx.instructor_dashboard.ecommerce.ExpiryCouponView = Backbone.View.extend({
        el: 'li#add-coupon-modal-field-expiry',
        events: {
            'click input[type="checkbox"]': 'clicked'
        },
        initialize: function() {
            $('li#add-coupon-modal-field-expiry input[name="expiration_date"]').hide();
            _.bindAll(this, 'clicked');
        },
        clicked: function (event) {
            if (event.currentTarget.checked) {
                this.$el.find('#coupon_expiration_date').show();
                this.$el.find('#coupon_expiration_date').focus();
            }
            else {
                this.$el.find('#coupon_expiration_date').hide();
            }
        }
    });

    $(function() {
        var $registration_code_status_form = $("form#set_regcode_status_form"),
            $lookup_button = $('#lookup_regcode', $registration_code_status_form),
            $registration_code_status_form_error = $('#regcode_status_form_error', $registration_code_status_form),
            $registration_code_status_form_success = $('#regcode_status_form_success', $registration_code_status_form);

        $( "#coupon_expiration_date" ).datepicker({
            minDate: 0
        });
        var view = new edx.instructor_dashboard.ecommerce.ExpiryCouponView();
        var request_response = $('.reports .request-response');
        var request_response_error = $('.reports .request-response-error');
        $('input[name="user-enrollment-report"]').click(function(){
            var url = $(this).data('endpoint');
            $.ajax({
             dataType: "json",
             url: url,
             success: function (data) {
                request_response.text(data['status']);
                return $(".reports .msg-confirm").css({
                  "display": "block"
                });
             },
             error: function(std_ajax_err) {
                request_response_error.text(gettext('Error generating grades. Please try again.'));
                return $(".reports .msg-error").css({
                  "display": "block"
                });
             }
           });
        });
        $lookup_button.click(function () {
            $registration_code_status_form_error.hide();
            $lookup_button.attr('disabled', true);
            var url = $(this).data('endpoint');
            var lookup_registration_code = $('#set_regcode_status_form input[name="regcode_code"]').val();
            if (lookup_registration_code == '') {
                $registration_code_status_form_error.show();
                $registration_code_status_form_error.text(gettext('Enter the enrollment code.'));
                $lookup_button.removeAttr('disabled');
                return false;
            }
            $.ajax({
                type: "GET",
                data: {
                    "registration_code"  : lookup_registration_code
                },
                url: url,
                success: function (data) {
                    var is_registration_code_valid = data.is_registration_code_valid;
                    var is_registration_code_redeemed = data.is_registration_code_redeemed;
                    var is_registration_code_exists = data.is_registration_code_exists;
                    $lookup_button.removeAttr('disabled');
                    if (is_registration_code_exists == 'false') {
                        $registration_code_status_form_error.hide();
                        $registration_code_status_form_error.show();
                        $registration_code_status_form_error.text(gettext(data.message));
                    }
                    else {
                        var actions_links = '';
                        var actions = [];
                        if (is_registration_code_valid == true) {
                            actions.push(
                                {
                                    'action_url': data.registration_code_detail_url,
                                    'action_name': gettext('Cancel enrollment code'),
                                    'registration_code': lookup_registration_code,
                                    'action_type': 'invalidate_registration_code'
                                }
                            );
                        }
                        else {
                            actions.push(
                                {
                                    'action_url': data.registration_code_detail_url,
                                    'action_name': gettext('Restore enrollment code'),
                                    'registration_code': lookup_registration_code,
                                    'action_type': 'validate_registration_code'
                                }
                            );
                        }
                        if (is_registration_code_redeemed == true) {
                            actions.push(
                                {
                                    'action_url': data.registration_code_detail_url,
                                    'action_name': gettext('Mark enrollment code as unused'),
                                    'registration_code': lookup_registration_code,
                                    'action_type': 'unredeem_registration_code'
                                }
                            );
                        }

                        for ( var i = 0; i < actions.length; i++ ) {
                            actions_links += '<a class="registration_code_action_link" data-registration-code="'+
                            actions[i]["registration_code"] +'" data-action-type="'+ actions[i]["action_type"] +'"' +
                            ' href="#" data-endpoint="' + actions[i]["action_url"] +'">' +
                            actions[i]["action_name"] + '</a>';
                        }
                        is_registration_code_redeemed = is_registration_code_redeemed ? 'Yes' : 'No';
                        is_registration_code_valid = is_registration_code_valid ? 'Yes' : 'No';

                        var registration_code_lookup_actions = $('<table width="100%" class="tb_registration_code_status">' +
                            '<thead> <th width="15%">' + gettext('Code') + '</th> <th width="20%">'+ gettext('Used') + '</th>'+
                            '<th width="14%">' + gettext('Valid') + '</th> <th>' + gettext('Actions') + '</th></thead><tbody><tr>'+
                            '<td>' + lookup_registration_code + '</td>' +
                            '<td>' + is_registration_code_redeemed +'</td>' +
                            '<td>' + is_registration_code_valid + '</td><td>' +
                            actions_links +
                            '</td></tr> </tbody> </table>'
                        );
                        // before insertAfter do this.
                        // remove the first element after the registration_code_status_form
                        // so it doesn't duplicate the registration_code_lookup_actions in the UI.
                        $registration_code_status_form.next().remove();

                        registration_code_lookup_actions.insertAfter($registration_code_status_form);
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    var data = $.parseJSON(jqXHR.responseText);
                    $lookup_button.removeAttr('disabled');
                    $registration_code_status_form_error.text(gettext(data.message));
                    $registration_code_status_form_error.show();
                }
            });
        });
        $("section#invalidate_registration_code_modal").on('click', 'a.registration_code_action_link', function(event) {
            event.preventDefault();
            $registration_code_status_form_error.attr('style', 'display: none');
            $lookup_button.attr('disabled', true);
            var url = $(this).data('endpoint');
            var action_type = $(this).data('action-type');
            var registration_code = $(this).data('registration-code');
            $.ajax({
                type: "POST",
                data: {
                    "registration_code": registration_code,
                    "action_type": action_type
                },
                url: url,
                success: function (data) {
                    $('#set_regcode_status_form input[name="regcode_code"]').val('');
                    $registration_code_status_form.next().remove();
                    $registration_code_status_form_error.hide();
                    $lookup_button.removeAttr('disabled');
                    $registration_code_status_form_success.text(gettext(data.message));
                    $registration_code_status_form_success.show();
                    $registration_code_status_form_success.fadeOut(3000);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    var data = $.parseJSON(jqXHR.responseText);
                    $registration_code_status_form_error.hide();
                    $lookup_button.removeAttr('disabled');
                    $registration_code_status_form_error.show();
                    $registration_code_status_form_error.text(gettext(data.message));
                }
            });
        });
    });
})(Backbone, $, _, gettext);
