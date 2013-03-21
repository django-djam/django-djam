;jQuery(function($){
    $('.dropdown-menu').find('label, select').click(
        function(e){
            e.stopPropagation();
        }
    );

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
});