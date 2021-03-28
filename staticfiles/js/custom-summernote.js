$(document).summernote({
    onpaste: function (e) {
        var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('Text');

        e.preventDefault();

        document.execCommand('insertText', false, bufferText);
    }
});