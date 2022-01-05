import crawler


# load data from cache if existent
avail = crawler.load_cache_index()
next = crawler.load_matchdata('next')
if not avail.empty:
    print(avail[['season', 'availMatchdays']])
    # activate & fill season inputs
    # check all availMatchdays are ints (not NULL):
    #     then, activate & fill matchday inputs
if not next.empty:
    print(next)
    # display next matches


# refresh cache & reload data
crawler.fetch_avail_seasons()
crawler.fetch_avail_matchdays()
avail = crawler.load_cache_index()
# (activate) & (re-)fill season/matchday inputs
# activate crawler button
crawler.fetch_next_matches()
next = crawler.load_matchdata('next')
# display (or update) next matches
