#!/usr/bin/python
# -*- coding: utf-8 -*-

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


class CustomTopo(Topo):
    "Topologia: h1,h2-s1-s2-h3 e s2-s3-h4,h5"

    def build(self):
        # Criação dos switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Criação dos hosts (endereços IP customizados)
        hosts = {
            'h1': self.addHost('h1', ip='192.168.0.1/28'),
            'h2': self.addHost('h2', ip='192.168.0.2/28'),
            'h3': self.addHost('h3', ip='192.168.0.3/28'),
            'h4': self.addHost('h4', ip='192.168.0.4/28'),
            'h5': self.addHost('h5', ip='192.168.0.5/28')
        }

        # Ligação host-switch
        self.addLink(hosts['h1'], s1)
        self.addLink(hosts['h2'], s1)
        self.addLink(hosts['h3'], s2)
        self.addLink(hosts['h4'], s3)
        self.addLink(hosts['h5'], s3)

        # Ligação entre switches
        self.addLink(s1, s2)
        self.addLink(s2, s3)


def add_mac_flows(net):
    """Adiciona regras OpenFlow simples baseadas em MAC."""

    switches = ['s1', 's2', 's3']
    # Limpa regras anteriores
    for s in switches:
        net[s].cmd('ovs-ofctl del-flows ' + s)
        net[s].cmd('ovs-ofctl add-flow ' + s + ' dl_type=0x806,actions=flood')  # ARP broadcast

    # Pega todos os hosts e seus MACs
    hosts = [net[h] for h in ('h1', 'h2', 'h3', 'h4', 'h5')]
    macs = {h.name: h.MAC() for h in hosts}

    pares = []
    for h_src in ('h1', 'h2', 'h3', 'h4', 'h5'):
        for h_dst in ('h1', 'h2', 'h3', 'h4', 'h5'):
            if h_src != h_dst:
                pares.append((h_src, h_dst))


    for src, dst in pares:
        m_src, m_dst = macs[src], macs[dst]
        for sw in switches:
            net[sw].cmd('ovs-ofctl add-flow ' + sw + ' dl_src=' + m_src + ',dl_dst=' + m_dst + ',actions=flood')
            net[sw].cmd('ovs-ofctl add-flow ' + sw + ' dl_src=' + m_dst + ',dl_dst=' + m_src + ',actions=flood')


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, controller=None, switch=OVSSwitch, autoSetMacs=True)
    net.start()
    info('\n=== Rede iniciada ===\n')

    info('Topologia: h1,h2-s1-s2-h3 e s2-s3-h4,h5\n')
    
    # Adiciona regras personalizadas
    add_mac_flows(net)

    # Teste básico de ping
    info('\n=== Testando conectividade (ping all) ===\n')
    net.pingAll()

    # CLI para inspeção manual
    CLI(net)
    net.stop()
    info('=== Rede finalizada ===\n')


if __name__ == '__main__':
    setLogLevel('info')
    run()
