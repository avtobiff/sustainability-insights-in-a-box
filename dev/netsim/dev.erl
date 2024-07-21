-module(dev).

-include_lib("econfd.hrl").
-include("econfd_errors.hrl").


-define(NS, 'urn:ietf:params:xml:ns:yang:ietf-poweff-level-1').
-define(IDLE_POWER, 1073741824).
-define(VAR_POWER, 10_000_000).
-define(MAX_POWER, 2147483648).

-record(state, {power_draw :: integer()}).


-on_load(on_load/0).

on_load() ->
    start(),
    ok.

start() ->
    start_log(),
    spawn(fun init/0).

start_log() ->
    Self = self(),
    proc_lib:spawn(fun() -> print_start(Self) end),
    receive
        print_started ->
            ok
    end.


init() ->
    print("waiting for confd to start~n", []),
    timer:sleep(1000),

    process_flag(trap_exit, true),
    ConfdPort = os:getenv("CONFD_IPC_PORT"),
    print("CONFD_IPC_PORT = ~p~n", [ConfdPort]),
    {ok, Daemon} = econfd:init_daemon(edge, ?CONFD_TRACE, user, none,
                                      {127,0,0,1}, ConfdPort),
    register(dev_dp, self()),

    TransCbs = #confd_trans_cbs{init = fun init_trans/1},
    ok = econfd:register_trans_cb(Daemon, TransCbs),

    DataCbs = #confd_data_cbs{callpoint = dev,
                              get_elem  = fun get_elem/2},
    ok = econfd:register_data_cb(Daemon, DataCbs),

    ok = econfd:register_done(Daemon),

    loop(#state{power_draw = ?IDLE_POWER}).


loop(#state{power_draw = PowerDraw}) ->
    receive
        {From, {get_elem, ['device-current-total-power-draw'| _]}} ->
            NewPowerDraw = power_draw(PowerDraw),
            From ! {dev_dp, {ok, {?C_UINT32, NewPowerDraw}}},
            loop(#state{power_draw = NewPowerDraw})
    end.


init_trans(_) -> ok.

get_elem(_Tx, Path) ->
    dev_dp ! {self(), {get_elem, Path}},
    receive
        {dev_dp, Res} ->
            Res
    after 1000 ->
              not_found
    end.


%% uint32
power_draw(PowerDraw)
 when PowerDraw < ?IDLE_POWER ->
    ?IDLE_POWER;
power_draw(PowerDraw)
  when PowerDraw < ?MAX_POWER ->
    ?IDLE_POWER + sign() * rand:uniform(?VAR_POWER);
power_draw(PowerDraw) ->
    %% PowerDraw >= ?MAX_POWER
    PowerDraw.


sign() ->
    case rand:uniform(2) of
        1 -> -1;
        _ -> 1
    end.


print(Fmt, Args) ->
    printer ! {print, Fmt, Args}.

print_start(From) ->
    register(printer, self()),
    {ok, Fd} = file:open("./" ++ atom_to_list(?MODULE) ++ ".log", [write]),
    From ! print_started,
    print_loop(Fd).

print_loop(Fd) ->
    receive
        {print, Fmt, Args} ->
            io:format(Fd, Fmt, Args),
            print_loop(Fd)
    end.
