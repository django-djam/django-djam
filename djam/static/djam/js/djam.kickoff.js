;

djam = window.djam || {};

jQuery(function($){
    $('.dropdown-menu').find('label, select').click(
        function(e){
            e.stopPropagation();
        }
    );

    $('select option[value=""]').text("");
    $('select[data-required="0"]').chosen({
        allow_single_deselect: true,
    });
    $('select[data-required="1"]').chosen();

    $('.add-popup').click(function(e){
        e.preventDefault();
        var $this = $(this),
            name = id_to_windowname($this.attr('rel')),
            href = this.href;
        if (href.indexOf('?') == -1) {
            href += '?is_popup=1';
        } else {
            href += '&is_popup=1';
        }
        window.open(
            href,
            name,
            'height=500,width=800,resizable=yes,scrollbars=yes'
        ).focus();
    });

    var finishAdd = djam.finishAdd = function(win, newId, newRepr){
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
    }

    if ($('body.model-list')) {
        var order_columns = $('th[data-order]'),
            order_field = $('#id_order');

        order_field.css('display', 'none');
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