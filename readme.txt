  124  163.309 MiB  163.309 MiB           1   @profile
   125                                         def main():
   126                                             #parse arguments
   127  164.363 MiB    1.055 MiB           1       memory_tracker.print_diff()
   128  164.363 MiB    0.000 MiB           1       parser = argparse.ArgumentParser()
   129  164.363 MiB    0.000 MiB           1       parser.add_argument("-c", "--config", required=True, type=str, help = "Full path to platform_config.json")
   130  164.363 MiB    0.000 MiB           2       parser.add_argument("-p", "--plot", required=False, action="store_true", 
   131  164.363 MiB    0.000 MiB           1                           help="Plot graph from outs only. Without run tests.")
   132  164.363 MiB    0.000 MiB           1       parser.add_argument("--clear", required=False, help="Clear outs log dir.")
   133  164.363 MiB    0.000 MiB           1       args = parser.parse_args()
   134                                             
   135                                             #init config and targets
   136  164.363 MiB    0.000 MiB           1       pconfig = cPlatformConfig(args.config)
   137  164.363 MiB    0.000 MiB           1       if pconfig.checkJson()==-1:
   138                                                 raise SystemExit
   139                                             
   140                                             # only plot graph
   141  164.363 MiB    0.000 MiB           1       if args.plot:
   142                                                 if pconfig.getVectorIsAll():
   143                                                     plot_inter_graph(pconfig)
   144                                                     #for attack in pconfig.getSupportedVectors():
   145                                                     #    pconfig.setVectorAttack(attack)
   146                                                     #    plot_graph_method(pconfig, graph_show=False)
   147                                                 else:
   148                                                     plot_graph_method(pconfig, graph_show=True)
   149                                             else: # run tests
   150  164.363 MiB    0.000 MiB           1           print("Run Tests")
   151  164.363 MiB    0.000 MiB           2           firewall = cFirewall(pconfig.getSSHNetworkFirewall(), 
   152  164.363 MiB    0.000 MiB           1                               admin_password=pconfig.getNetworkFirewallAdmin())
   153  164.434 MiB    0.070 MiB           1           firewall.init_xf(pconfig.getFirewallSettings())
   154  164.434 MiB    0.000 MiB           1           firewall.disconnect()
   155                                         
   156  164.434 MiB    0.000 MiB           1           if pconfig.getVectorIsAll():
   157  164.434 MiB    0.000 MiB           1               attacks = pconfig.getSupportedVectors()
   158  948.164 MiB    0.000 MiB           3               for attack in attacks:
   159  566.895 MiB    1.652 MiB           2                   memory_tracker.print_diff()
   160  566.895 MiB    0.000 MiB           2                   pconfig.setVectorAttack(attack)
   161  566.895 MiB    0.000 MiB           2                   if args.clear: clean_work_space(pconfig)        
   162  569.848 MiB  738.797 MiB           2                   make_test(pconfig)
   163  942.266 MiB  761.516 MiB           2                   plot_graph_method(pconfig, graph_show=False)
   164  948.164 MiB   14.422 MiB           2                   memory_tracker.print_diff()
   165  239.016 MiB -709.148 MiB           1               plot_inter_graph(pconfig)
   166  254.508 MiB   15.492 MiB           1               memory_tracker.print_diff()
   167                                                 else:
   168                                                     if args.clear: clean_work_space(pconfig)       
   169                                                     make_test(pconfig)
   170                                                     plot_graph_method(pconfig, graph_show=True)
