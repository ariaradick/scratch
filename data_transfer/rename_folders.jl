paths_in = String[]
paths_out = String[]
parent_dir = "/data/2/GFDL-LARGE-ENSEMBLES/TFTEST/"

for i in 1:10
    n = 3(i-1)
    n1 = lpad(n+1,2,"0")
    n2 = lpad(n+3,2,"0")
    for j in 1:3
        n_ens_arch = lpad(j,2,"0")
        n_ens_decp = lpad(n+j,2,"0")
        push!(paths_in, "SPEAR_c192_o1_Hist_AllForc_IC1921_K50_ens_$(n1)_$(n2)/pp_ens_$(n_ens_arch)")
        push!(paths_in, "SPEAR_c192_o1_Scen_SSP585_IC2011_K50_ens_$(n1)_$(n2)/pp_ens_$(n_ens_arch)")
        push!(paths_out, "SPEAR_c192_o1_Hist_AllForc_IC1921_K50/pp_ens_$(n_ens_decp)")
        push!(paths_out, "SPEAR_c192_o1_Scen_SSP585_IC2011_K50/pp_ens_$(n_ens_decp)")
    end
end

commands = String[]

for i in eachindex(paths_in)
    push!(commands, "ln -s $(parent_dir)$(paths_in[i]) $(parent_dir)$(paths_out[i])")
end

using DelimitedFiles: writedlm
writedlm("symlink_ensembles.sh", commands)