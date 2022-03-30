from env import SCEnv
from examples.smac.policy import MaskedLogitPolicy
from torchrl.envs import TransformedEnv, ObservationNorm
from torchrl.modules import ProbabilisticTDModule, OneHotCategorical, QValueActor
from torch import nn

if __name__ == "__main__":
    # create an env
    env = SCEnv("8m")

    # reset
    td = env.reset()
    print("tensordict after reset: ")
    print(td)

    # apply a sequence of transforms
    env = TransformedEnv(env, ObservationNorm(0, 1, standard_normal=True))

    # Get policy
    policy = nn.LazyLinear(env.action_spec.shape[-1])
    policy_wrap = MaskedLogitPolicy(policy)
    policy_td_module = ProbabilisticTDModule(
        module=policy_wrap,
        spec=None,
        in_keys=["observation", "available_actions"],
        out_keys=["action"],
        distribution_class=OneHotCategorical,
        save_dist_params=True,
    )

    # Test the policy
    policy_td_module(td)
    print(td)
    print('param: ', td.get("action_dist_param_0"))
    print('action: ', td.get("action"))
    print('mask: ', td.get("available_actions"))
    print('mask from env: ', env.env._env.get_avail_actions())

    # check that an ation can be performed in the env with this
    env.step(td)
    print(td)

    # we can also have a regular Q-Value actor
    print('\n\nQValue')
    policy_td_module = QValueActor(
        policy_wrap, spec=None,
        in_keys=["observation", "available_actions"],
        out_keys=["actions"])
    td = env.reset()
    policy_td_module(td)
    print('action: ', td.get("action"))
    env.step(td)
    print('next_obs: ', td.get("next_observation"))