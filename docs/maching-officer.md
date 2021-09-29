# Matching officer flow

## I. Keyword Processing
a) Existed
1. First, get all the new keywords = last inserted - last run.
2. Get delete keywords = lat run - last inserted
3. Process check new keywords for all old articles.
   1. If contain new keywords -> append to extracted keywords of new_article.
   2. If empty extracted keyword before => process NLP.
      1. If officer exist and not in system_exclude_officer => add officer to officers field
      2. If officer exist and in system_exclude_officer => add officer to article_exclude_officers field
4. Process check delete keywords for all old articles.
   1. Remaining keywords = extracted keywords - deleted keywords.
   2. If remaining keywords is Empty => remove relation (both officers and article_exclude_officers)
   3. Update extracted keywords <= remaining keywords.

b) New:
1. First, get all keywords = last inserted.
2. Process check all keywords for all new articles with null extracted keywords. 
   1. If contain new keywords -> append to extracted keywords of new_article. Process NLP.
      1. If officer exist and not in system_exclude_officer => add officer to officers field
      2. If officer exist and in system_exclude_officer => add officer to article_exclude_officers field 
   2. If not contain new keywords -> save empty list extracted keywords.

## II. Exclude officer processing
1. First get all the new exclude officers = last inserted - last run
2. Get deleted exclude officers = last run - last inserted
3. Process check new exclude officers:
   1. If article_officers contain new_system_exclude_officer: 
      1. Remove new_exclude_officer in article_officers 
      2. Add new_exclude_officer to article_exclude_officer
4. Process check delete exclude officers:
   1. If article_exclude_officers contain deleted_system_exclude_officer: 
      1. Remove delete_exclude_officer in article_exclude_officers 
      2. Add delete_exclude_officer to article_officers