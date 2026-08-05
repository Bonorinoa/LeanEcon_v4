"""Provider adapter package.

Architecture rule (Gate 3 decision 6 and docs/gate3/06): the adapter
package is the only place that may import vendor SDKs or HTTP clients for
provider egress. Enforced by tests/test_architecture_boundary.py.
"""
