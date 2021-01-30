import click, logging, asyncio, time
from .api import Api
from .const import TWO_FACTOR_AUTH_METHODS
import asyncio

_logger = logging.getLogger(__name__)
logging.basicConfig(format='%(name)-10s %(levelname)-8s %(message)s')

uefyApi = None


#pylint: disable=no-value-for-parameter
try:
    loop = asyncio.get_running_loop()
except:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

class MyContext(click.Context):
    def __init__(self):
        self.uefyApi = None

@click.group(chain=True)
@click.pass_context
@click.option('--debug/--no-debug', prompt='activate debug', default=False)
def cli(ctx, debug):
    _logger.debug('cli: %s, %s' %(type(ctx), ctx))
    if(ctx.obj is None):
        ctx.obj = MyContext()
    _logger.parent.setLevel(logging.DEBUG if debug else logging.INFO)
    _logger.setLevel(logging.DEBUG if debug else logging.INFO)

@cli.command()
@click.pass_context
@click.option('--username', prompt='eufy security username', default=None)
@click.option('--password', prompt='eufy security password', default=None)
@click.option('--tfa', prompt='preferred two factor authentication method (EMAIL, SMS, PUSH)', default='EMAIL')
def login(ctx, username, password, tfa):
    _logger.debug('Username: %s, Password: %s, tfa: %s' % (username, password, tfa))
    try:
        ctx.parent.obj.uefyApi = Api(username=username, password=password, preferred2FAMethod=TWO_FACTOR_AUTH_METHODS[tfa])
        response = asyncio.run(ctx.parent.obj.uefyApi.authenticate())
        click.echo('Response: %s' % response)
        if(response == 'OK'):
            click.echo('Token: %s' % ctx.parent.obj.uefyApi.token)
            click.echo('Token_expire: %s' % ctx.parent.obj.uefyApi.token_expire_at)
            click.echo('Domain: %s' % ctx.parent.obj.uefyApi.domain)
        elif(response == 'send_verify_code'):
            verificationCode = click.prompt('Enter verification code: %s')
            response = asyncio.run(ctx.parent.obj.uefyApi.sendVerifyCode(verificationCode))
            click.echo('Response: %s' % response)
            if(response == 'OK'):
                click.echo('Token: %s' % ctx.parent.obj.uefyApi.token)
                click.echo('Token_expire: %s' % ctx.parent.obj.uefyApi.token_expire_at)
                click.echo('Domain: %s' % ctx.parent.obj.uefyApi.domain)
    except Exception as e:
        _logger.exception(e)
        pass
    pass

@cli.command()
@click.pass_context
@click.option('--token', prompt='eufy token', default=None, required=False)
@click.option('--token_expire_at', prompt='eufy token expiratio timestamp', default=None, required=False)
@click.option('--domain', prompt='eufy domain', default=None, required=False)
def session(ctx, token, domain, token_expire_at):
    ctx.parent.obj.uefyApi = Api(token=token, domain=domain, token_expire_at=int(token_expire_at))

@cli.command()
@click.pass_context
def devices(ctx):
    try:
        asyncio.run(ctx.parent.obj.uefyApi.update())
        for deviceSn, device in ctx.parent.obj.uefyApi.devices.items():
            click.echo(device)
        for stationSn, station in ctx.parent.obj.uefyApi.stations.items():
            click.echo(station)
        # print(ctx.parent.obj.uefyApi.devices.values())
    except Exception as e:
        _logger.exception(e)
    pass

@cli.command()
@click.pass_context
@click.option('--serial', prompt='eufy device serial id', default=None, required=False)
def monitor(ctx, serial):
    asyncio.run(ctx.parent.obj.uefyApi.update(device_sn=serial))
    async def update_print(attributes):
        for attribute in attributes:
            # _logger.debug(attribute)
            click.echo('updated: %s, from \'%s\' to \'%s\'' % attribute)
    if(serial in ctx.parent.obj.uefyApi.devices):
        ctx.parent.obj.uefyApi.devices[serial].subscribe([], update_print)
        try:
            for i in range(0,60*5):
                asyncio.run(ctx.parent.obj.uefyApi.update(device_sn=serial))
                time.sleep(1)
        except Exception as e:
            _logger.exception(e)
    else:
        click.echo('unknown serial: %s' % serial)

if __name__ == '__main__':
    cli()
    loop.run_until_complete()
    loop.close()