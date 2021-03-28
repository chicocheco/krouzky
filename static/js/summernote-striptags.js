(function (factory) {
    /* global define */
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    } else if (typeof module === 'object' && module.exports) {
        // Node/CommonJS
        module.exports = factory(require('jquery'));
    } else {
        // Browser globals
        factory(window.jQuery);
    }
}(function ($) {
    $.extend($.summernote.plugins, {
        'rawtext': function (context) {
            let $note = context.layoutInfo.note;
            $note.on('summernote.paste', function (e, evt) {
                let bufferText = ((evt.originalEvent || evt).clipboardData || window.clipboardData).getData('Text');
                evt.preventDefault();
                setTimeout(function () {
                    document.execCommand('insertText', false, bufferText);
                }, 100);
            });
        }
    });
}));

// How to use
/*
(function ($) {
   $(function () {
      $('.summernote').summernote({
         toolbar: [
            ['custom', ['striptags']],
         ],
         striptags: {
            stripTags: ['style'],
            stripAttributes: ['border', 'style'],
            onAfterStripTags: function ($html) {
               $html.find('table').addClass('table');
               return $html;
            }
         }
      });
   });
})(jQuery);
 */