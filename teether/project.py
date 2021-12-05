import logging
from collections import defaultdict
import traceback

from teether.cfg.cfg import CFG
from teether.cfg.disassembly import generate_BBs
from teether.cfg.opcodes import external_data
from teether.evm.evm import run, run_symbolic
from teether.evm.exceptions import IntractablePath, ExternalData, SymbolicError
from teether.explorer.forward import ForwardExplorer
from teether.slicing import interesting_slices, slice_to_program
from teether.util.z3_extra_util import concrete


def load(path):
    with open(path) as infile:
        return Project(bytes.fromhex(infile.read().strip()))


def load_json(path):
    import json
    with open(path) as infile:
        return Project.from_json(json.load(infile))


class Project(object):
    def __init__(self, code, cfg=None):
        self.code = code
        self._prg = None
        self._cfg = cfg
        self._writes = None

        self._func_entries = dict()
        self.xcall = list()

    @property
    def func_entries(self):
        if not self._func_entries:
            self._func_entries = self._get_func_entry()
        return self._func_entries

    @property
    def writes(self):
        if not self._writes:
            self._analyze_writes()
        return self._writes

    @property
    def symbolic_writes(self):
        return self.writes[None]

    @property
    def cfg(self):
        if not self._cfg:
            self._cfg = CFG(generate_BBs(self.code))
        return self._cfg

    @property
    def prg(self):
        if not self._prg:
            self._prg = {ins.addr: ins for bb in self.cfg.bbs for ins in bb.ins}
        return self._prg

    def to_json(self):
        return {'code': self.code.hex(), 'cfg': self.cfg.to_json()}

    @staticmethod
    def from_json(json_dict):
        code = bytes.fromhex(json_dict['code'])
        cfg = CFG.from_json(json_dict['cfg'], code)
        return Project(code, cfg)

    def run(self, program):
        return run(program, code=self.code)

    def run_symbolic(self, path, inclusive=False):
        ctx = {'xcall':self.xcall}
        return run_symbolic(self.prg, path, self.code, ctx=ctx, inclusive=inclusive)

    def is_valid_path(self, path):
        path = path[:-1]
        for cnt, nid in enumerate(path):
            bb = self.cfg._bb_at[nid]
            last_ins = bb.ins[-1].op
            is_last_bb_ins = True if cnt == len(path) -1 else False
            if last_ins in (0x00, 0xf3, 0xfd, 0xfe, 0xff) and not is_last_bb_ins:
                # print(hex(last_ins))
                return False, path[:cnt+1], path[cnt+1:]
        return True, None, None

    def get_constraints(self, instructions, args=None, inclusive=False, find_sstore=False, invests=None, looplimit = 3, side_rewards=[]):
        # known
        # for call_i, call_p, call_r in side_rewards:
        #     yield call_i, call_p, call_r
        
        # only check instructions that have a chance to reach root
        instructions = [ins for ins in instructions if (0 in ins.bb.ancestors | {ins.bb.start})]
        if not instructions:
            return
        imap = {ins.addr: ins for ins in instructions}

        exp = ForwardExplorer(self.cfg)
        if args:
            slices = [s + (ins,) for ins in instructions for s in interesting_slices(ins, args, reachable=True)]
        else:
            # Are we looking for a state-changing path?
            if find_sstore:
                sstores = self.cfg.filter_ins('SSTORE', reachable=True)
                slices = [(sstore, ins) for sstore in sstores for ins in instructions]
            else:
                slices = [(ins,) for ins in instructions]
            
            # if invests:
            #     slices = [(invest, ins,) for invest in invests for ins in instructions]
        
        try_cnt = 0
        for path in exp.find(slices, looplimit=looplimit, avoid=external_data):
            try_cnt += 1
            # print("find a path", path)
            # for bb in path:
            #     print(self.cfg._bb_at[bb])
            # if 'CALLER' not in self.cfg._bb_at[path[-2]] 
            if try_cnt > 32:
                yield None, None, None

            # res, error_path, remainingpath = self.is_valid_path(path)
            # if not res:
            #     bad_path = error_path + [remainingpath[0]]
            #     dd = self.cfg.data_dependence(error_path[-1])
            #     if not any(i.name in ('MLOAD', 'SLOAD') for i in dd):
            #         ddbbs = set(i.bb.start for i in dd)
            #         bad_path_start = next((j for j, i in enumerate(bad_path) if i in ddbbs), 0)
            #         bad_path = bad_path[bad_path_start:]
            #     logging.info("Bad path: %s" % (', '.join('%x' % i for i in bad_path)))
            #     exp.add_to_blacklist(bad_path)
            #     print('error: path')
            #     continue
    
            logging.debug('Path %s', ' -> '.join('%x' % p for p in path))

            try:
                ins = imap[path[-1]]
                # print('finish static generate')
                yield ins, path, self.run_symbolic(path, inclusive)
            except IntractablePath as e:
                # fail_cnt += 1
                print("Fail", e)
                bad_path = [i for i in e.trace if i in self.cfg._bb_at] + [e.remainingpath[0]]
                dd = self.cfg.data_dependence(self.cfg._ins_at[e.trace[-1]])
                if not any(i.name in ('MLOAD', 'SLOAD') for i in dd):
                    ddbbs = set(i.bb.start for i in dd)
                    bad_path_start = next((j for j, i in enumerate(bad_path) if i in ddbbs), 0)
                    bad_path = bad_path[bad_path_start:]
                logging.info("Bad path: %s" % (', '.join('%x' % i for i in bad_path)))
                exp.add_to_blacklist(bad_path)
                # print('error: path')
                continue
            except ExternalData:
                print('error: exter')
                traceback.print_exc()
                continue
            except SymbolicError:
                print('error: sym')
                traceback.print_exc()
                continue
            except Exception as e:
                # traceback.print_exc()
                print('error:', e)
                logging.exception('Failed path due to %s', e)
                continue
            # else:
            #     traceback.print_exc()
            #     continue
            
                

    def traver_cfg(instruction, threshold=256):
        exp = ForwardExplorer(self.cfg)
        slices = [(instruction,)]
        return exp.detect_loop(slices, threshold, avoid=[])


    def _get_func_entry(self):
        func_entries = dict()
        for bb in self.cfg.bbs:
            if len(bb.ins) < 5:
                continue
            if bb.ins[0].name == 'JUMPDEST':
                # fallback
                func_entries['fallback'] = bb.start
                break
            if bb.ins[-3].name and 'EQ' and bb.ins[-2].name.startswith('PUSH') and bb.ins[-1].name == 'JUMPI':
                # choose a func entry
                if bb.ins[-5].name == 'PUSH4' and bb.ins[-4].name == 'DUP2':
                    func_sig = bb.ins[-5].arg.hex()
                elif bb.ins[-5].name == 'DUP1' and bb.ins[-4].name == 'PUSH4':
                    func_sig = bb.ins[-4].arg.hex()
                else:
                    continue
                entry   = int(bb.ins[-2].arg.hex(), 16)
                func_entries[func_sig] = entry
        return func_entries

    def get_func_sig(self, path):
        FALLBACK = 'fallback'
        '''
        DUP1      
        PUSH4     0x27e235e3# func_sig
        EQ        
        PUSH2     addr
        JUMPI    
        '''
    
        for sig, entry in self.func_entries.items():
            if entry in path:
                return sig
        print("NONNOON func sig")
        return FALLBACK


    def get_paths(self, instructions, args=None, inclusive=False, find_sstore=False):
        # only check instructions that have a chance to reach root
        instructions = [ins for ins in instructions if 0 in ins.bb.ancestors | {ins.bb.start}]
        if not instructions:
            return
        imap = {ins.addr: ins for ins in instructions}

        exp = ForwardExplorer(self.cfg)
        if args:
            slices = [s + (ins,) for ins in instructions for s in interesting_slices(ins, args, reachable=True)]
        else:
            # Are we looking for a state-changing path?
            if find_sstore:
                sstores = self.cfg.filter_ins('SSTORE', reachable=True)
                slices = [(sstore, ins) for sstore in sstores for ins in instructions]
            else:
                slices = [(ins,) for ins in instructions]
        for path in exp.find(slices, avoid=external_data):
            logging.debug('Path %s', ' -> '.join('%x' % p for p in path))
            try:
                ins = imap[path[-1]]
                yield ins, path
            except IntractablePath as e:
                bad_path = [i for i in e.trace if i in self.cfg._bb_at] + [e.remainingpath[0]]
                dd = self.cfg.data_dependence(self.cfg._ins_at[e.trace[-1]])
                if not any(i.name in ('MLOAD', 'SLOAD') for i in dd):
                    ddbbs = set(i.bb.start for i in dd)
                    bad_path_start = next((j for j, i in enumerate(bad_path) if i in ddbbs), 0)
                    bad_path = bad_path[bad_path_start:]
                logging.info("Bad path: %s" % (', '.join('%x' % i for i in bad_path)))
                exp.add_to_blacklist(bad_path)
                continue
            except ExternalData:
                continue
            except Exception as e:
                logging.exception('Failed path due to %s', e)
                continue

    def gen_paths(self, target):
        exp = ForwardExplorer(self.cfg)
        slices = [(target,)]
        paths = list()
        for path in exp.find(slices, avoid=external_data):
            # logging.debug('Path %s', ' -> '.join('%x' % p for p in path))
            # path[-1] = target.bb.start
            paths.append(path[:-1])
        return paths



    def _analyze_writes(self):
        sstore_ins = self.cfg.filter_ins('SSTORE')
        print('#',sstore_ins, '#')
        self._writes = defaultdict(set)
        for store in sstore_ins:
            for bs in interesting_slices(store):
                bs.append(store)
                prg = slice_to_program(bs)
                path = sorted(prg.keys())
                try:
                    r = run_symbolic(prg, path, self.code, inclusive=True)
                except IntractablePath:
                    logging.exception('Intractable Path while analyzing writes')
                    continue
                addr = r.state.stack[-1]
                if concrete(addr):
                    self._writes[addr].add(store)
                else:
                    self._writes[None].add(store)
        self._writes = dict(self._writes)

    def get_writes_to(self, addr):
        concrete_writes = set()
        if concrete(addr) and addr in self.writes:
            concrete_writes = self.writes[addr]
        return concrete_writes, self.symbolic_writes
