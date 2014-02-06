$(document).ready(function () {
	// Wrap each word in a span.
	$('.masthead .logo a').each(function(){ 
	 var text = $(this).text().split(' ');
	 for( var i = 0, len = text.length; i < len; i++ ) { 
		 text[i] = '<span class="word-' + i + '">' + text[i] + '</span>'; 
		} 
		$(this).html(text.join(' '));
	});
});
