-module(scrap_SUITE).
-include_lib("common_test/include/ct.hrl").
-compile(export_all).
-define(ZOMATO_URL, "http://www.zomato.com/ncr/restaurants").

all() -> [get_total_pages, generate_links].


init_per_testcase(_, Config) ->
	Config.

end_per_testcase(_, _Config) ->
	ok.


get_total_pages(_Config) ->
	application:start(inets),
	application:start(crypto),
	application:start(asn1),
	application:start(public_key),
	application:start(ssl),
	{ok, {_V, _H, Body}} = httpc:request(get, {"http://www.zomato.com/ncr/restaurants", []}, [], []) ,
	451 = client:get_total_pages(Body).


generate_links(_Config) ->
	io:format("URL is:~s~n", [?ZOMATO_URL]).
%%	{ok, 451} = client:generate_links(?ZOMATO_URL).

