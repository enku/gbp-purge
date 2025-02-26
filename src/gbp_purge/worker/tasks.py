def purge_machine(machine: str):
    from gbp_purge.gateway import GBPGateway

    gateway = GBPGateway()

    gateway.purge(machine)
