---
layout: single
permalink: /cv-news-record/
author_profile: true
---

<style>
.news-record-details {
  margin-bottom: 1rem;
  border: 1px solid #eaecef;
  border-radius: 6px;
  overflow: hidden;
}
.news-record-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  list-style: none;
  font-weight: 500;
  background: #f6f8fa;
  font-size: 1.1rem;
}
.news-record-summary:hover {
  background: #eceff2;
}
.news-record-summary::-webkit-details-marker { display: none; }
.news-record-summary::before {
  content: '▶';
  margin-right: 0.5rem;
  font-size: 0.75em;
  transition: transform 0.2s;
  color: #57606a;
}
.news-record-details[open] .news-record-summary::before {
  transform: rotate(90deg);
}
.news-record-enter {
  font-size: 0.9rem;
  color: #0969da;
  text-decoration: none;
  white-space: nowrap;
}
.news-record-enter:hover { text-decoration: underline; }
.news-record-content {
  padding: 1rem;
  border-top: 1px solid #eaecef;
  background: #fff;
}
.news-record-content iframe {
  width: 100%;
  min-height: 600px;
  border: 1px solid #eaecef;
  border-radius: 6px;
}
</style>

{% if site.data.news_record and site.data.news_record.entries %}
{% for entry in site.data.news_record.entries reversed %}
{% assign html_url = site.baseurl | append: '/news_record/' | append: entry.folder | append: '/' | append: entry.html | replace: ' ', '%20' %}
<details class="news-record-details">
  <summary class="news-record-summary">
    <span>{{ entry.label }}</span>
    <a href="{{ html_url }}" target="_blank" rel="noopener" onclick="event.stopPropagation()" class="news-record-enter">Enter</a>
  </summary>
  <div class="news-record-content">
    <iframe data-src="{{ html_url }}" title="{{ entry.label }}" loading="lazy"></iframe>
  </div>
</details>
{% endfor %}

<script>
(function() {
  document.querySelectorAll('.news-record-details').forEach(function(details) {
    details.addEventListener('toggle', function() {
      if (details.open) {
        var iframe = details.querySelector('iframe[data-src]');
        if (iframe) {
          iframe.src = iframe.getAttribute('data-src');
          iframe.removeAttribute('data-src');
        }
      }
    });
  });
})();
</script>
{% else %}
<p>No record yet. Please add configs in <code>_data/news_record.yml</code> ，then add HTML file under <code>news_record/</code> </p>
{% endif %}
