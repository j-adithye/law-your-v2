# BNS Phase 6: test questions

Run each one with:

```
python manage.py search "<question>"
```

Examples of expected section numbers are from memory. Check them against your own data before counting a result as a miss.

## Questions

| #   | Question                                                           | Expected sections                     | What it tests                                 |
| --- | ------------------------------------------------------------------ | ------------------------------------- | --------------------------------------------- |
| 1   | What is the punishment for murder?                                 | 103 (or 101)                          | plain question                                |
| 2   | What is the difference between murder and culpable homicide?       | 100, 101, 105                         | look-alike sections                           |
| 3   | Someone hit me with a stick and broke my arm                       | 117 (or 115, 118)                     | vague, everyday wording                       |
| 4   | A man on a bike grabbed my phone and rode off                      | 304                                   | snatching vs theft vs robbery                 |
| 5   | A group of ten people attacked a house at night and looted it      | 310 (or 309)                          | dacoity vs robbery                            |
| 6   | He threatened to hurt my family unless I paid him money            | 308 (or 351)                          | extortion vs intimidation                     |
| 7   | My husband and in-laws keep harassing me for dowry                 | 85 (or 80)                            | cruelty vs dowry death                        |
| 8   | A man keeps following a woman and messaging her after she said no  | 78                                    | stalking, no legal terms used                 |
| 9   | An employee was trusted with company money and spent it on himself | 316                                   | criminal breach of trust, no legal terms used |
| 10  | What is the colour of an apple                                     | any random section with high distance | off-topic                                     |

## Results

| #   | Expected    | Rank   | Best distance | Notes            | Phase 7 Rank |
| --- | ----------- | ------ | ------------- | ---------------- | ------------ |
| 1   | 103         | 2      | 0.4067(104)   |                  | 1            |
| 2   | 100,101,105 | 2,1,4  | 0.4075(101)   |                  | None         |
| 3   | 117         | missed | 0.7280(114)   | vauge qn         | None         |
| 4   | 304         | 4      | 0.7137(134)   |                  | None         |
| 5   | 310         | 2      | 0.6184(331)   |                  | None         |
| 6   | 308         | missed | 0.6537(32)    | simialar         | None         |
| 7   | 85          | 2      | 0.6298(80)    |                  | None         |
| 8   | 78          | 1      | 0.6142(78)    |                  | None         |
| 9   | 316         | 1      | 0.6474(316)   |                  | None         |
| 10  | none        | -      | 0.915(141)    | expected outcome | None         |
