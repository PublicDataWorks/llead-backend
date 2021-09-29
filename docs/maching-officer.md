# Matching officer flow

a) Existed
1. First, get all the new keywords = last inserted - last run.
2. Get delete keywords = lat run - last inserted
3. Process check new keywords for all old articles.
   1. If contain new keywords -> append to extracted keywords of new_article.
   2. If empty extracted keyword before => process NLP.
4. Process check delete keywords for all old articles.
   1. Remaining keywords = extracted keywords - deleted keywords.
   2. If remaining keywords is Empty => remove relation.
   3. Update extracted keywords <= remaining keywords.

b) New:
1. First, get all keywords = last inserted.
2. Process check all keywords for all new articles with null extracted keywords.
3. If contain new keywords -> append to extracted keywords of new_article. Process NLP.
4. If not contain new keywords -> empty list extracted keywords.