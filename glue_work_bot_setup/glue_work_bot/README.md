## Instructions

Here are the ways you can configure the Glue Work Tracker Bot:

1. In `glue_work_bot_config.yml`, you can configure the bot in a few ways:
    1. `retrieved_days` – set the number of retrieved days.
    2. `top_count` – set the number of contributors shown at the top of each category.
    3. `repository` – optionally collect data from a separate repository.
    4. `excluded_users` – exclude users/bots from the search by name.

2. In the `workflows` folder, edit `run_glue_work_bot.yml` to configure the cron schedule and adjust how often it runs.