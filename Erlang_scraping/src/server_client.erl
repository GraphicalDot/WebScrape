-module(server_client).
-behaviour(gen_server).
-compile(export_all).
-import(utils, [start_applications/0, get_page_count/0, get_page_body/1, add_restro_details/2]).
-import(mnesia_utils, [start_mnesia/1]).

-define(ZOMATO_URL, "http://www.zomato.com/ncr/restaurants").
-record(link, {url='', page_no, body=""}).


%%%%%%%%%%%%%%%%% CLIENT APIS %%%%%%%%%%%%%%%%%%%%%%

start_scraping() ->
	io:format("~nINSIDE START SCRAPING~n"),
	mnesia_utils:start_mnesia([node()]),
	utils:start_applications(),
	{Status, Total_pages} = utils:get_page_count(),
	if 
		Status =:= success -> 
			try lists:foreach(fun(Loop_count) ->
				io:format("N is:~p~n", [Loop_count]),
				{Stat, Body} = utils:get_page_body(Loop_count),
				if 
					Stat =:= success ->	
						Link = #link{url=?ZOMATO_URL, page_no=Loop_count, body=Body},
						start_scraping_process(Link);
					Stat =:= error ->
						throw(error_in_page_request)				
				end
			     end, lists:seq(1, Total_pages))
			catch 
				throw:error_in_page_request ->
					{error, "Some problem occured in some page request"}
			end;
		Status =:= error ->
			{error, "Some problem occured in the request"}
	end.


start_scraping_process(Link) ->
	{ok, Pid} = gen_server:start_link(?MODULE, [], []),
	gen_server:call(Pid, {details, Link}).
	


%%%%%%%%%%%%%%%%% SERVER APIS %%%%%%%%%%%%%%%%%%%%%

init([]) -> {ok, []}.

handle_cast({details, Link=#link{}}, Links) ->
	{noreply, [Link|Links]}.

handle_call({details, Link=#link{}}, _From, Links) ->
        utils:add_restro_details(Link),
        {reply, ok, [Link|Links]}.

handle_info(Msg, Links) ->
        io:format("Unexpected message: ~p~n", [Msg]),
        {noreply, Links}.

code_change(_OldVsn, State, _Extra) ->
        {ok, State}.

terminate(normal, _) ->
        io:format("Terminating~n"),
        ok.

