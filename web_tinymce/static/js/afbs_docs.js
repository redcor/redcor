$("input.parent_doc").on("click", function() {
    var selected_num = this.id.split('_')[2];
    $("input.parent_doc").each(function(i, button) {
        var num = $(button).attr('id').split('_')[2];
        var child_docs_container = $("#child_docs_container_" + num);
        if (num == selected_num) {
            $(button).attr('style', 'background:green;')
            $(child_docs_container).show();
        }
        else {
            $(button).attr('style', '')
            $(child_docs_container).hide();
        }
    });
});

$("select.child_doc_selection").on("change", function() {
    var num = this.id.split('_')[3];
    var link = $("select#child_doc_selection_" + num).val();
    if (link) {
        $("#link-text").val($("select#child_doc_selection_" + num + " option:selected").text());
        $("#link-external").val(link);
    }
    else {
        $("#link-text").val("");
        $("#link-external").val("");
    }
});
