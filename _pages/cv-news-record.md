---
layout: single
title: "CV News Record"
permalink: /cv-news-record/
author_profile: true
---

本页面按周展示整理的 CV 相关资讯与笔记，内容来自 `news_record` 目录下按日期命名的文件夹。

{% if site.data.news_record and site.data.news_record.entries %}
{% for entry in site.data.news_record.entries reversed %}
<section class="news-record-entry" style="margin-bottom: 2.5rem;">
  <h2 id="{{ entry.folder }}" style="font-size: 1.35rem; margin-top: 1.5rem; margin-bottom: 0.75rem;">{{ entry.label }}</h2>
  <iframe
    src="{{ site.baseurl }}/news_record/{{ entry.folder }}/{{ entry.html | replace: ' ', '%20' }}"
    title="{{ entry.label }}"
    style="width: 100%; min-height: 600px; border: 1px solid #eaecef; border-radius: 6px;"
    loading="lazy"
  ></iframe>
</section>
{% endfor %}
{% else %}
<p>暂无记录。请在 <code>_data/news_record.yml</code> 中配置条目，并在 <code>news_record/</code> 下放置对应文件夹与 HTML 文件。</p>
{% endif %}
