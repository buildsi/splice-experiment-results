---
layout: page
title: Log Viewer
css: ["about.css", "animate.css", "morphext.css"]
js: ["morphext.min.js", "about.js"]
permalink: /logviewer/
---

<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.23.0/themes/prism-coy.min.css" rel="stylesheet" type="text/css">

<h4 id="title"></h4>

<div class="row">
  <a id="backlink" href="">Back to experiment</a><br>
  <a id="otherlog" href=""></a>
</div>

<div class="row">
  <div class="col-md-12">
<pre><code class="language-shell" id="log">
</code></pre>
  </div>
</div>
<div class="row">
  <p>View related logs</p>
  <div class="col-md-12 links">
  </div>
</div>

<script src="//code.jquery.com/jquery-2.2.4.min.js" integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44=" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.23.0/prism.min.js"></script>
<script>
var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
    return false;
};

$(document).ready(function(){

   var url = getUrlParameter('url');
   var type = getUrlParameter('type');
   var name = getUrlParameter('name');
   $("#title").text(name + " " + type)

   // Prepare "back to experiment" link
   parts = url.split("/")
   backlink = parts.splice(1, parts.length -2).join("/")
   console.log(backlink)
   backlink = "{{ site.url }}{{ site.baseurl }}/" + backlink + "/"
   $("#backlink").attr("href", backlink)
   othertype = "out"
   if (type == "out") {
       othertype = "err"
   }
   var otherlog = "{{ site.baseurl }}/logviewer/?name=" + name + "&type=" + othertype + "&url=" + url
   $("#otherlog").attr("href", otherlog)
   $("#otherlog").html(name + "." + othertype)

   fullurl = "{{ site.url }}{{ site.baseurl }}" + url

   // Keep track of others to render 
   $.getJSON(fullurl, function(data) {

      console.log(data)
      var others = [] 

      $.each(data, function(key, values){
        if (key == name) {
           var logfile = values[type]
           $.get(backlink + logfile, function(text) {
               $("#log").html(text)  
            })
        } else {
            $.each(values, function(k, v){
               if (k != type) {
                   others.push({"name": key, "type": k, "url": url, "file": v})   
               }
            })
        }
      })
      
      // Add quick links for other related logs
      console.log(others)
      $.each(others, function(i, other){
          $(".links").append("<a href='{{ site.baseurl }}/logviewer/?name=" + other['name'] + "&type=" + other['type']+ "&url=" + other['url']+ "'>" + other['file'] + "</a><br>")
      })

   }).fail(function() {
        $("#log").html("<p>These logs are empty.</p>")   
   })
   console.log(type)
   console.log(name)
   
})
</script>
