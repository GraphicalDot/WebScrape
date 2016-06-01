-module(utils).
-compile(export_all).
-import(mnesia_utils, [add_record_in_mnesia/22]).

-define(ZOMATO_URL, "http://www.zomato.com/ncr/restaurants").
-record(link, {url='', page_no, body=""}).
-record(restro_details, {eatery_id, eatery_photo_link, eatery_name, eatery_address, eatery_cuisine,   eatery_cost, eatery_type, eatery_delivery_time, eatery_minimum_order, eatery_rating, eatery_title, eatery_trending, eatery_total_reviews, eatery_highlights, eatery_popular_reviews, location, eatery_buffet_price, eatery_buffet_details, eatery_recommended_order, eatery_known_for, eatery_area_or_city, eatery_opening_hours}).


start_applications() ->
	application:start(inets),
        application:start(crypto),
        application:start(asn1),
        application:start(public_key),
        application:start(ssl).


get_page_count() ->
	case httpc:request(get, {?ZOMATO_URL, []}, [], []) of
		{ok, {_V, _H, Body}} ->
			Binary_body = unicode:characters_to_binary(Body),
			Total_pages = list_to_integer(binary_to_list(lists:nth(1, binary:split(lists:nth(2, binary:split(Binary_body, <<"Page 1 of ">>)), <<" \"><div>">>)))),
			{success, Total_pages};
		{error, Reason} ->
			{error, Reason}
	end.		
 

get_page_body(Page) ->
	case httpc:request(get, {"http://www.zomato.com/ncr/restaurants?page=" ++ integer_to_list(Page), []}, [], []) of
                {ok, {_V, _H, Body}} ->
                        Binary_body = unicode:characters_to_binary(Body),
	       		{success, Binary_body};
                {error, Reason} ->
                       {error, Reason}

        end.


add_restro_details(Link=#link{}) ->
        Body = lists:nth(2, binary:split(Link#link.body, <<"js-search-result-li even  status 1">>)),
        add_details(Body, 1),
        ok.


add_details([], _) ->
        ok;

add_details(Body, Restro_num) ->
	New_splitted = binary:split(Body, <<"js-search-result-li even  status 1">>),
        io:format("~n~nRestro num:~p~n~n", [Restro_num]),
        if
                Restro_num =< 30 ->
                        add_details_in_mnesia(lists:nth(1, New_splitted)),
                        add_details(lists:nth(2, New_splitted), Restro_num + 1);
                Restro_num >= 31 ->
                        add_details([], Restro_num)
        end.


add_details_in_mnesia(Body) ->

	%% get eatery id 
        Eatery_id = lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"data-res_id=">>)), <<" data-position=">>)),
	io:format("Eatery id:~s~n", [Eatery_id]), 

	%% get eatery url
	case has_section(<<"<a class=">>, Body) of
		true ->
			Eatery_url = lists:nth(1, binary:split(lists:nth(2, binary:split(lists:nth(2, binary:split(Body, <<"<a class=">>)), <<"href=">>)), <<" title=">>));
		false ->
			Eatery_url = ""
	end,
	io:format("Eatery url:~s~n", [Eatery_url]), 
	

	%% get eatery photo link
	case has_section(<<"search_left_featured">>, Body) of 
		true ->
			Eatery_photo_link = lists:nth(1, binary:split(lists:nth(2, binary:split(lists:nth(2, binary:split(Body, <<"search_left_featured">>)), <<"a href=">>)), <<"class=">>));
		false ->
			Eatery_photo_link = ""
	end,
	io:format("Eatery_photo link:~s~n", [Eatery_photo_link]),


	%% get eatery name
	case has_section(<<" top-res-box-name left">>, Body) of
		true ->
			Eatery_name = lists:nth(1, binary:split(lists:nth(2, binary:split(lists:nth(2, binary:split(lists:nth(2, binary:split(Body, <<" top-res-box-name left">>)), <<"title">>)), <<">">>)), <<"</a>">>));
		false ->
			Eatery_name = ""
	end,
	io:format("Eatery name:~s~n", [Eatery_name]),


	%% get eatery address
	case has_section(<<"search-result-address zdark">>, Body) of 
		true ->
			Eatery_address = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"search-result-address zdark">>)), <<"</div>">>)), <<">">>));
		false ->
		Eatery_address = ""
	end,
	io:format("Eatery address:~s~n", [Eatery_address]),

	
	%% get eatery cuisine
	case has_section(<<"res-cuisine mt2 clearfix">>, Body) of 
		true ->
			Eatery_cuisine = lists:nth(1, binary:split(lists:nth(2, binary:split(lists:nth(2, binary:split(Body, <<"res-cuisine mt2 clearfix">>)), <<"title=">>)), <<">">>));
		false ->
			Eatery_cuisine = ""
	end,
	io:format("Eatery cuisine:~s~n", [Eatery_cuisine]),


	%% get eatery cost
	case has_section(<<"res-cost clearfix">>, Body) of 
		true ->	
			Eatery_cost = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(lists:nth(2, binary:split(Body, <<"res-cost clearfix">>)), <<"search-grid-right-text">>)), <<"</span>">>)), <<">">>));
		false ->
			Eatery_cost = "0"
	end,
	io:format("Eatery cost:~s~n", [Eatery_cost]),


	%% get eatery type
	case has_section(<<"res-snippet-small-establishment">>, Body) of
		true ->
			Eatery_type = lists:nth(2, binary:split(lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"res-snippet-small-establishment">>)), <<"</a>">>)), <<"href">>)), <<">">>));
		false ->
			Eatery_type = ""
	end,
	io:format("Eatery type:~s~n", [Eatery_type]),


	%% get eatery minimum order cost
	case has_section(<<"del-min-order">>, Body) of
                true ->
                        Eatery_min_order = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"del-min-order">>)), <<"</div>">>)), <<"</span>">>));
                false ->
                        Eatery_min_order = "0"
        end,
        io:format("Eatery min order cost:~s~n", [Eatery_min_order]),


	%% get eatery delivery time
	case has_section(<<"del-time">>, Body) of
                true ->
                        Eatery_del_time = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"del-time">>)), <<"</div>">>)), <<"</span>">>));
                false ->
                        Eatery_del_time = "0"
        end,
        io:format("Eatery del time:~s~n", [Eatery_del_time]),


	%% get eatery rating
	Dict = dict:new(),
        Splitted_body = lists:nth(2, binary:split(Body, <<"search_result_rating col-s-3  clearfix">>)),
	case has_section(<<"rating-for">>, Splitted_body) of
		true ->
			Rating = lists:nth(2, binary:split(lists:nth(2, binary:split(lists:nth(1, binary:split(Splitted_body, <<"</div>">>)), <<"rating-for">>)), <<">">>));
		false ->
			Rating = ""
	end,
	io:format("RATING:~s~n", [Rating]),

	case has_section(<<"rating-votes">>, Splitted_body) of
		true ->
			Votes = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Splitted_body, <<"rating-votes">>)), <<"</span>">>)), <<">">>));
		false ->
			Votes = ""
	end,
	io:format("VOTES:~s~n", [Votes]),
        
	Rating_dict = dict:store("rating", Rating, Dict),
        Eatery_rating = dict:store("votes", Votes, Rating_dict),
%%	io:format("EATERY RATING:~p~n", [Eatery_rating]),

	%% get eatery title
	case has_section(<<"result-title">>, Body) of
		true ->
			Eatery_title = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"result-title">>)), <<"</a>">>)), <<">">>));
		false ->
			Eatery_title = ""
	end,
	io:format("Eatery title:~s~n", [Eatery_title]),


	%% get eatery trending
	case has_section(<<"srp-collections">>, Body) of
                true ->
                        Eatery_trending = lists:nth(2, binary:split(lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"srp-collections">>)), <<"</a>">>)), <<"href">>)), <<">">>));
                false ->
                        Eatery_trending = ""
        end,
        io:format("Eatery trending:~s~n", [Eatery_trending]),


	%% get eatery reviews count
	case has_section(<<"ResCard_Reviews">>, Body) of 
		true ->
			Eatery_reviews_count = lists:nth(2, binary:split(lists:nth(1, binary:split(lists:nth(2, binary:split(Body, <<"ResCard_Reviews">>)), <<"</a>">>)), <<">">>));
		false -> 
			Eatery_reviews_count = "0"
	end,
	io:format("Eatery reviews count:~s~n", [Eatery_reviews_count]),

	
	%% add record to mnesia
	F = fun() -> mnesia:write(#restro_details{eatery_id=Eatery_id, eatery_photo_link=Eatery_photo_link, eatery_name=Eatery_name, eatery_address=Eatery_address, eatery_cuisine=Eatery_cuisine, eatery_cost=Eatery_cost, eatery_type=Eatery_type, eatery_delivery_time=Eatery_del_time, eatery_minimum_order=Eatery_min_order, eatery_rating=Eatery_rating, eatery_title=Eatery_title, eatery_trending=Eatery_trending, eatery_total_reviews=Eatery_reviews_count, eatery_highlights="", eatery_popular_reviews="", location="", eatery_buffet_price="", eatery_buffet_details="", eatery_recommended_order="", eatery_known_for="", eatery_area_or_city="", eatery_opening_hours=""}) end,
        mnesia:activity(transaction, F).


%	mnesia_utils:add_record_in_mnesia(Eatery_id, Eatery_photo_link, Eatery_name, Eatery_address, Eatery_cuisine, Eatery_cost, Eatery_type, Eatery_del_time, Eatery_min_order, Eatery_rating, Eatery_title, Eatery_trending, Eatery_reviews_count, none, none, none, none, none, none, none, none).



has_section(Pattern, Body) ->
	M = length(binary:matches(Body, Pattern)),
        if M =:= 1 -> true;
           true -> false
        end.

