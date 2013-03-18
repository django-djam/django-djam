;jQuery(function($){
    $('.dropdown-menu').find('label, select').click(
        function(e){
            e.stopPropagation();
        }
    );
});