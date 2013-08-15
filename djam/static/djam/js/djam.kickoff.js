;

var djam = window.djam || {};

jQuery(function($) {
    $('.dropdown-menu').find('label, select').click(
        function(e) {
            e.stopPropagation();
        }
    );

    $('select option[value=""]').text("");
    $('select[data-required="0"]').chosen({
        allow_single_deselect: true,
        width: 'auto'
    });
    $('select[data-required="1"]').chosen({width: 'auto'});

    function addLinkPopup(e) {
        e.preventDefault();
        var $this = $(this),
            name = id_to_windowname($this.attr('rel')),
            href = this.href;
        if (href.indexOf('?') === -1) {
            href += '?is_popup=1';
        } else {
            href += '&is_popup=1';
        }
        window.open(
            href,
            name,
            'height=500,width=800,resizable=yes,scrollbars=yes'
        ).focus();
    }
    $('.add-popup').click(addLinkPopup);

    djam.finishAdd = function(win, newId, newRepr){
        // newId and newRepr are expected to have previously been escaped by
        // django.utils.html.escape.
        var newId = html_unescape(newId),
            newRepr = html_unescape(newRepr),
            opt = $("<option selected value='" + newId + "'>" + newRepr + "</option>"),
            name = windowname_to_id(win.name),
            elem = $("#" + name);
        elem.append(opt);

        // Tell Chosen this has been updated
        elem.trigger('liszt:updated');

        win.close();
    };

    // Maps content type ids to choices/addLinks.
    var contentTypes = djam.contentTypes = {};

    function getContentType(id, callback) {
        var opts = contentTypes[id];
        if (opts === undefined) {
            opts = contentTypes[id] = {
                objectIdFields: [],
                choices: [],
                addUrl: ''
            };
            if (id !== "") {
                $.getJSON(djam.genRelURL + id + '/',
                    function(data) {
                        opts.choices = data.choices;
                        opts.addUrl = data.add_url;
                        if (opts.choices.length === 0) {
                            opts.inputEle = $('<input type="text" />');
                        } else {
                            opts.inputEle = $('<select></select>');
                            $.each(opts.choices, function(index, item) {
                                opts.inputEle.append($('<option value="' + item[0] + '">' + item[1] + '</option>'));
                            });
                        }
                        if (opts.addUrl) {
                            opts.addLink = $('<a href="' + opts.addUrl + '" class="btn add-popup"><i class="icon-plus"></i></a>');
                        }
                        callback(opts);
                    }
                );
            }
        } else {
            callback(opts);
        }
    }

    $('.djam-genrel').each(function(index, ele) {
        var $ele = $(ele),
            objectId = $ele.find('input[value]'),
            contentType = $ele.find('select'),
            required = contentType.data('required') === "1" ? true : false,
            values = {};
        values[contentType.val()] = objectId.val()

        function storeValue() {
            values[contentType.val()] = $(this).val();
        }

        function displayObjectInput(opts) {
            var inputEle = opts.inputEle.clone(),
                addLink = opts.addLink ? opts.addLink.clone() : null;
            inputEle.attr('id', objectId.attr('id'));
            inputEle.attr('name', objectId.attr('name'));
            if (required) {
                inputEle.attr('required', 'required');
            }

            contentType.next().nextAll().remove();
            $ele.append(inputEle);
            inputEle.val(values[contentType.val()] || "");

            if (opts.choices.length > 0) {
                inputEle.chosen({width: 'auto'});
            }
            inputEle.change(storeValue);

            if (addLink) {
                addLink.attr('rel', objectId.attr('id'));
                $ele.append(addLink);
                addLink.click(addLinkPopup);
            }
        }

        contentType.chosen({width: 'auto'}).change(function() {
            getContentType(contentType.val(), displayObjectInput);
        });
        contentType.change();
    });

    if ($('body.model-list')) {
        var order_columns = $('th[data-order]'),
            order_field = $('#id_order');

        order_columns.css('cursor', 'pointer');

        order_columns.click(function(){
            var $this = $(this),
                order = $this.data('order'),
                desc_next = !$this.hasClass('desc');

            next_val = (desc_next ? '-' : '') + order;
            order_field.val(next_val);
            order_field.parent().submit();
        });
    };

    var btnAddon = $('<span class="input-group-btn"><a href="javascript://" class="btn btn-default"></a></span>')
    // time inputs.
    var timeInputs = $('input[type=time]'),
        timeAddon = btnAddon.clone();
    timeAddon.find('a').append('<i class="icon-time"></i></a>')
    timeInputs.attr('type', 'text');
    timeInputs.wrap('<div class="bootstrap-timepicker input-group"></div>');
    timeInputs.parent().append(timeAddon.clone());
    timeInputs.timepicker({
        template: 'dropdown',
        showMeridian: false,
        showInputs: false,
        defaultTime: false
    });


    // date inputs.
    var dateInputs = $('input[type=date]'),
        dateAddon = btnAddon.clone();
    dateAddon.find('a').append('<i class="icon-calendar"></i></a>')
    dateInputs.attr('type', 'text');
    dateInputs.wrap('<div class="input-group date"></div>');
    dateInputs.parent().append(dateAddon);
    dateInputs.parent().datepicker({
        format: 'yyyy-mm-dd'
    });


    // Helper functions for popup handling. From Django.

    function html_unescape(text) {
        // Unescape a string that was escaped using django.utils.html.escape.
        text = text.replace(/&lt;/g, '<');
        text = text.replace(/&gt;/g, '>');
        text = text.replace(/&quot;/g, '"');
        text = text.replace(/&#39;/g, "'");
        text = text.replace(/&amp;/g, '&');
        return text;
    }

    // IE doesn't accept periods or dashes in the window name, but the element IDs
    // we use to generate popup window names may contain them, therefore we map them
    // to allowed characters in a reversible way so that we can locate the correct 
    // element when the popup window is dismissed.
    function id_to_windowname(text) {
        text = text.replace(/\./g, '__dot__');
        text = text.replace(/\-/g, '__dash__');
        return text;
    }

    function windowname_to_id(text) {
        text = text.replace(/__dot__/g, '.');
        text = text.replace(/__dash__/g, '-');
        return text;
    }
});