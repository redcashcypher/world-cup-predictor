Drop national flag assets here, named by FIFA country code, e.g.:

  ar.svg   (Argentina)
  fr.svg   (France)
  br.svg   (Brazil)

`src/data/fixtures.mock.json` references flags as `/flags/{code}.svg`.
Until real assets are added, `FlagPlaceholder.jsx` renders a bordered
initials box so the layout never breaks.
