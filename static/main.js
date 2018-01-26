$(function (){
    /**
     * Mostly JS with a dash of JQuery
     */
    var img =  document.getElementById('decode-field') ?
        document.getElementById('decode-field') :
        document.getElementById('photo-loaded');

    var msg = document.getElementById('message');

    if(img){
        // Both Decode and Encode use this function
        img.addEventListener('change', showPreview);
    }

    // Decode Animation
    if(msg)
    {
        // Avoiding use of .html() for security
        var backup = $('#message');
        backup.css('display', 'none');
        var letters = backup.text();
        var field = $('#message-show');
        for(var i = 0; i < letters.length; i++)
        {
            if(i % 7  == 0)
            {
                field.append("<span class='let-7'>" + letters[i] + "</span>");
            }
            else if(i % 3 == 0)
            {
                field.append("<span class='let-3'>" + letters[i] + "</span>");
            }
            else if(i % 5 == 0)
            {
                field.append("<span class='let-5'>" + letters[i] + "</span>");
            }
            else
            {
                field.append("<span class='let-0'>" + letters[i] + "</span>");
            }
        }
    }
    // So we can see our message in plain HTML
    var hide = $('#')
    var exit = $('#exit');
    exit.on('click', function(){
        $('#flashes').css('display', 'none');
    });

});

// Image preview
function showPreview(e){
        var preview = document.getElementById('preview');
        preview.style.display = 'block';
        preview.style.margin = 'auto auto';
        preview.style.height = '600px';
        preview.src = URL.createObjectURL(e.target.files[0]);
}
