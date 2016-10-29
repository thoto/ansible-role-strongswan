# ansible-role-strongswan
ansible role to setup strongswan IPsec including public key authentication

## Variables

This role fetches its configuration from two variables providing a list of
X.509 certificate authorities inside the `ipsec_cas` variable and connections
using those CAs inside `ipsec_conns` variable. Thereby you can configure
connections and enforce security parameters at a central point without
caring about missing configuration of connections at per host level and
enable easy 1:n or n:n connections.

Also defaults for all connections may be changed by altering the
`ipsec_conn_default` variable. Therefore you are able to adjust crypto
defaults without altering every single host and keep configuration
as short as possible.

### CAs

#### Properties of a CA

_TL;DR_: see [examples section](#examples)!

* `name`: any name identifying the CA in a connection definition
* `file`: CA certificate to upload to IPsec server
* `id_prefix`: ID DN prefix. E.g. if your DN on your certificate should be 
  `O=example.net, OU=ipsec, CN=foo.example.net` on host `foo.example.net`
  your `id_prefix` variable should go `O=example.net, OU=ipsec`. Providing
  it inside the CA definition lowers signing complexity and the number of
  keys to be generated, since just a single key and certificate has to be
  generated and issued per CA and host.
* `ca_host`: host on which the signing authority script is placed.
* `ca_host_user`: which user to become on `ca_host` using raw sudo. This
  uses shell sudo instead of the `become` facility included in ansible because
  there is no clean and secure way to build an according entry inside the
  `sudoers` file without permitting full shell access with CA users privileges
  and therefore possibly leaking the CAs private key. This is caused by the
  way ansible modules get executed on the remote host.
* `ca_sign_command`: command to execute accepting a PKCS.10 CSR on standard
  input and returning a DER encoded CA signed certificate on standard output.
  The according DN is passed as the last parameter of the command.
* `ca_sign_command_args`: additional arguments to pass to `ca_sign_command`

#### Notes on CA key signing

The following shell script provides a simple way to perform ca signing tasks:

```shell
#!/bin/sh
CAKEY="/etc/ipsec.d/private/fooca-cacert-key.der"
CACERT="/etc/ipsec.d/cacerts/fooca-cacert.der"
ipsec pki --issue --type pkcs10 --cakey ${CAKEY} --cacert ${CACERT} \
	--digest sha256 --dn "$1"
```

This is a quite simple implementation of a CA, maybe insecure because there
is no validation and correction. Multiple CAs may be handled by a similar
script using the `ca_sign_command_args`.

The following entry in `/etc/sudoers` secures this script to prevent access
to the CAs private key (replace `johndoe` by your users name):

```shell
Cmnd_Alias CASIGN = /usr/local/sbin/casign-dtis
johndoe ALL = NOPASSWD: CASIGN
```

### Connections
_TL;DR_: see [examples section](#Examples)!

* `name`: identifier of the connection
* `left`/`right`: FQDN as string or list of FQDNs specifying the hosts to be
  connected. Every host on one side gets connected to all of the others side
  but not to the ones on the same side.
* `crypto`: dict of crypto parameters to use.
* `ca`: name of the CA to be used

Multiple other options can be found at
[`defaults/main.yml`](./defaults/main.yml) which should be self-explanatory
and adjust various parameters of the connection to be generated.
(e.g. connection margin and life parameters, compression, etc.)
See [strongswan documentation](https://wiki.strongswan.org/projects/strongswan/wiki/ConnSection) for more information.

### other options
* `ipsec_default_key_size`: default size of key if none is given in `ipsec_cas`


## Examples

### CA
```yaml
- ipsec_cas:
  - name: fooca
    file: fooca-cacert.der
    id_prefix: "O=ansible, OU=ipsecca"
    ca_host: localhost
    ca_host_user: root
    ca_sign_command: /usr/local/sbin/casign-fooca
```

### connection
```yaml
- ipsec_conns:
  - name: foo-connection
    left: zeus.example.net
    right:
      - poseidon.example.net
      - apollon.example.net
    crypto:
      esp: aes128gcm16-sha512
      ike: aes256gcm16-sha512-sha384-ecp521
    ca: fooca
```
