# Algorithm TP/FP report

Target repository: https://github.com/nodejs/node
The project has 3618 contributors.

By using the original Bird implementation with threshold of 0.98, over 31,000 results were observed. The developers csv file contained 4764 entries.

By manually verifying the first 1,000 entries from the Bird implementation, we observed 990 FPs and 9 TPs. This is a very high FP ratio compared to TPs.

# Own implementation

My own proposal for the implementation is just using Levenshtein distance. I used Grok 4 for development assistance for the script.

Usage: ``py duplicates_grok.py <input csv> <threshold 0-100> <thread count> <output csv>``

> Note: You might need to move the csv file to the same folder as the py file for this to work.

After manually verifying 500 rows, we got 451 TPs and 47 FPs using 60 as threshold. 60 threshold was used just so we could get at least 1000 results for observation, similar to the verification process of the Bird method.

Comparing to the original Bird implementation, 99% vs 9.4% FP rate is significantly lower, but still not perfect. Using 75 as threshold, we get an FP rate of 0% with 350 entries.

Notes:
- After going <75 threshold, the accuracy lowered significantly.
- This does not work well for users who have same domain in their email, such as ``victor123@chromium.org`` vs ``helen123@chromium.org``