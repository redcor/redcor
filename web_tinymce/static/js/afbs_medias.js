$("select#media").on("change", function() {
    var link = $("select#media").val();
    if (link) {
        $("#link-text").val($("select#media option:selected").text());
        $("#link-external").val(link);
    }
    else {
        $("#link-text").val("");
        $("#link-external").val("");
    }
});
