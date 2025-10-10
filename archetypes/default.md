+++
id = "{{ now.Format "060102150405" }}"
date = '{{ .Date }}'
draft = true
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
