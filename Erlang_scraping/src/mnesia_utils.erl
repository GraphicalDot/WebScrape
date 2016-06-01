-module(mnesia_utils).
-compile(export_all).
-record(restro_details, {eatery_id, eatery_photo_link, eatery_name, eatery_address, eatery_cuisine,   eatery_cost, eatery_type, eatery_delivery_time, eatery_minimum_order, eatery_rating, eatery_title, eatery_trending, eatery_total_reviews, eatery_highlights, eatery_popular_reviews, location, eatery_buffet_price, eatery_buffet_details, eatery_recommended_order, eatery_known_for, eatery_area_or_city, eatery_opening_hours}).


start_mnesia(Nodes) ->
%%        mnesia:wait_for_tables([restro_details], 5000),
        mnesia:stop(),
        ok = mnesia:delete_schema(Nodes),
        ok = mnesia:create_schema(Nodes),
        mnesia:start(),
        {atomic, ok} = mnesia:create_table(restro_details,
                            [{attributes, record_info(fields, restro_details)},
                             {disc_copies, Nodes}]).


%add_record_in_mnesia(Eatery_id, Eatery_photo_link, Eatery_name, Eatery_address, Eatery_cuisine, Eatery_cost, Eatery_type, Eatery_del_time, Eatery_min_order, Eatery_rating, Eatery_title, Eatery_trending, Eatery_reviews_count, Eatery_highlights, Eatery_popular_reviews, Eatery_location, Eatery_buffet_price, Eatery_buffet_details, Eatery_recommended_order, Eatery_known_for, Eatery_area_or_city, Eatery_opening_hours) ->
%	io:format("INSIDE ADD RECORD IN MNESIA~n"),
%	F = fun() -> mnesia:write(#restro_details{eatery_id=Eatery_id, eatery_photo_link=Eatery_photo_link, eatery_name=Eatery_name, eatery_address=Eatery_address, eatery_cuisine=Eatery_cuisine, eatery_cost=Eatery_cost, eatery_type=Eatery_type, eatery_delivery_time=Eatery_del_time, eatery_minimum_order=Eatery_min_order, eatery_rating=Eatery_rating, eatery_title=Eatery_title, eatery_trending=Eatery_trending, eatery_total_reviews=Eatery_reviews_count, eatery_highlights=Eatery_highlights, eatery_popular_reviews=Eatery_popular_reviews, location=Eatery_location, eatery_buffet_price=Eatery_buffet_price, eatery_buffet_details=Eatery_buffet_details, eatery_recommended_order=Eatery_recommended_order, eatery_known_for=Eatery_known_for, eatery_area_or_city=Eatery_area_or_city, eatery_opening_hours=Eatery_opening_hours}) end,
%       mnesia:activity(transaction, F).


