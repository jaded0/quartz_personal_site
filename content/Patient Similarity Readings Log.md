---
title: "Patient Similarity Readings Log"
tags:
- paper_notes
---
 #work/patientsim 


```dataview
list file.title + dateformat(file.ctime, " yy-MM-dd") + " - " + file.tags
from #work/patientsim and #paper_notes
sort file.ctime desc
```
