paths_in = String[]
paths_out = String[]

for i in 1:10
    n = 3(i-1)
    n1 = lpad(n+1,2,"0")
    n2 = lpad(n+3,2,"0")
    for j in 1:3
        n_ens = lpad(j,2,"0")
        push!(paths_in, "SPEAR_c192_o1_Hist_AllForc_IC1921_K50_ens_$(n1)_$(n2)/pp_ens_$(n_ens)")
        push!(paths_in, "SPEAR_c192_o1_Scen_SSP585_IC2011_K50_ens_$(n1)_$(n2)/pp_ens_$(n_ens)")
        push!(paths_out, "SPEAR_c192_o1_Hist_AllForc_IC1921_K50/pp_ens_$(n+j)")
        push!(paths_out, "SPEAR_c192_o1_Scen_SSP585_IC2011_K50/pp_ens_$(n+j)")
    end
end

mv_commands = String[]
rm_commands = String[]

for i in eachindex(paths_in)
    push!(mv_commands, "mv $(paths_in[i])/* $(paths_out[i])")
    push!(rm_commands, "rm $(paths_in[i])")
end

using DelimitedFiles: writedlm
writedlm("test.txt", mv_commands)