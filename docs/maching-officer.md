# Matching officer flow

## I. Keyword Processing
a) Existed
1. First, get all the new keywords = last inserted - last run.
2. Get delete keywords = lat run - last inserted
3. Process check new keywords for all old articles.
   1. If contain new keywords and the position is new -> create new matched_sentence. Process NLP.
      1. If officer exist and not in system_exclude_officer => add officer to the above matched_sentence officers
      2. If officer exist and in system_exclude_officer => add officer to the above matched_sentence excluded_officers
   2. If contain new keywords and the position is existed append keyword to existed matched_sentence.
4. Process check deleted keywords for all old articles.
   1. Loop through all matched_sentence contain deleted keywords
      1. Remaining keywords = extracted keywords - deleted keywords.
      2. If remaining keywords is Empty => delete object
      3. If remaining keywords is not empty => Update extracted keywords = remaining keywords.

b) New:
1. First, get all keywords = last inserted.
2. Process check all keywords for all new articles with `is_processed = False`. 
   1. If contain new keywords -> create new matched_sentence. Process NLP.
      1. If officer exist and not in system_exclude_officer => add officer to officers field
      2. If officer exist and in system_exclude_officer => add officer to article_exclude_officers field 
3. Set `is_processed = true` => save.

## II. Exclude officer processing
1. First get all the new exclude officers = last inserted - last run
2. Get deleted exclude officers = last run - last inserted
3. Process check new exclude officers:
   1. If matched_sentence contain new_system_exclude_officer: 
      1. Remove new_exclude_officer in officers 
      2. Add new_exclude_officer to exclude_officers
4. Process check delete exclude officers:
   1. If matched_sentence contain deleted_system_exclude_officer: 
      1. Remove delete_exclude_officer in exclude_officers 
      2. Add delete_exclude_officer to officers