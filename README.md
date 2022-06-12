# youtube-mass-upload

<h1><b>Prerequisites</b></h1>

<ul>
  <li>Python 2.6 or greater.</li>

<li>Pip package management tool to download dependencies.</li>

<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="pip install -r requirements.txt"><pre class="notranslate"><code>pip install -r requirements.txt
</code></pre></div>
  
<li>Get client_secrets.json file from Google API Console.</li>

</ul>


<h1><b>ytUpload.py</b></h1>

Application will upload multiple videos with thumbnails, video description, and keywords to YouTube.

Refer to https://developers.google.com/youtube/v3/determine_quota_cost for API quota costs.

Request quota extension if uploading more than 3+ videos per day:<br> 
https://support.google.com/youtube/contact/yt_api_form?hl=en
