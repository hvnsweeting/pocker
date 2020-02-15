# pocker
Docker implemented in Python (3)

> What I cannot create, I do not understand - Richard Feynman

Inspired by [bocker](https://github.com/p8952/bocker)

## TODO
Write the code

### Issues
- The original bocker script was written in 2015, all the docker API changed since then.
- `bocker pull` no longer works due to above reason. Use https://github.com/moby/moby/blob/master/contrib/download-frozen-image-v2.sh instead.
  The script requires `golang` and `jq` dependencies. Both are replacible by pure Python (jq -> json, golang -> platform just to get arch `amd64`)
- This fork https://github.com/frohoff/bocker works, which uses above download script.
