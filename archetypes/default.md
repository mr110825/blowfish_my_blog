+++
id = "{{ now.Format "060102150405" }}"
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
tags = []
+++
